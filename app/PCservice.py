# PCservice.py
import time
import socket
from PCdata import PCdata
from PClog import PClog
from PCfunctions import PCfuncs
from PCmessage import PCmessage
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta

class PCservice():
    def __init__(self, device_id):
        # 功能模块初始化
        self.PC_data = PCdata()
        self.PC_log = PClog()
        self.PC_funcs = PCfuncs()
        self.PC_message = PCmessage()
        self.device_id = device_id
        self.PC_logger = self.PC_data.get_main_logger()

        # bemfa参数
        self.server_ip = 'bemfa.com'
        self.server_port = 8344

    # 更新日志显示名称
    def set_logger(self):
        # 获取设备名称
        self.logger_name = self.PC_data.get_device_device_name(self.device_id)
        # 检查是否重复，重复则使用设备id
        if self.PC_log.check_duplicate_logger(self.logger_name):
            self.logger_name = self.device_id
        self.logger = self.PC_log.get_logger(self.logger_name, level=self.logger_level)
        self.PC_data.update_device_service_logger(self.device_id, self.logger)
        self.PC_logger.info(f"设备{self.device_id}的日志显示名称已设置为：[{self.logger_name}]")

    # 开启定时ping
    def add_ping_job(self):
        if self.PC_funcs.checkbool(self.PC_data.get_device_device_ping_enabled(self.device_id)):
            try:
                self.scheduler.add_job(self.ping_check, 'interval', seconds=self.PC_data.get_device_device_ping_time(self.device_id), next_run_time=datetime.now(), id='ping_job')
                self.logger.info("Ping服务已启动")
            except Exception as e:
                self.logger.error("ping服务启动失败：" + str(e))

    # 关闭定时ping
    def remove_ping_job(self):
        if self.scheduler.get_job('ping_job'):
            try:
                self.scheduler.remove_job('ping_job')
                self.logger.info("Ping服务已停止")
            except Exception as e:
                self.logger.error("Ping服务停止失败："+str(e))
    
    # 定时ping检测设备状态
    def ping_check(self):
        try:
            # ping结果
            ping_result = self.PC_funcs.pcping(self.device_id)
            self.logger.debug(ping_result)
            if 'Reply' in ping_result or 'receive on' in ping_result:
                self.is_power_off = False
                new_state = ["在线","on"]
            elif 'timed out' in ping_result or 'receive off' in ping_result:
                # 如果不是离线状态，则第一次检测到离线时，再ping一次减少误判
                if not self.is_power_off:
                    self.is_power_off = True
                    self.ping_check()
                    return
                new_state = ["离线","off"]
            else:
                new_state = ["未知","unknown"]
            # 获取存储的设备状态
            pc_state = self.PC_data.get_device_status(self.device_id)
            # 如果不一致则更新
            if pc_state != new_state:
                self.PC_data.update_device_status(self.device_id, new_state)
                self.logger.info(f"设备状态更新：{new_state[0]}")
                self.PC_message.send_message(self.device_id, f"状态更新：{new_state[0]}")
        except Exception as e:
            self.logger.error("ping出错：" + str(e))

    # 添加定时开关机任务
    def schedule_add_plans_job(self):
        if self.PC_funcs.checkbool(self.PC_data.get_device_schedule_enabled(self.device_id)):
            self.logger.debug("正在添加定时开关机任务")
            plans = self.PC_data.get_device_schedule_plans(self.device_id)
            for plan in plans:
                plan_id = self.PC_funcs.trans_str(plan.get('id'))
                try:
                    if self.PC_funcs.checkbool(plan.get('enabled')):
                        plan_type = self.PC_funcs.trans_str(plan.get('type'))
                        plan_action = self.PC_funcs.trans_str(plan.get('action'))
                        plan_remind = self.PC_funcs.checkbool(plan.get('remind'))
                        plan_remind_advance = int(plan.get('advance', 5))
                        if plan_type == 'datetime':
                            plan_datetime_str = plan.get('datetime')  #字符串类型
                            next_run_str = plan_datetime_str
                            plan_datetime_trans = datetime.strptime(plan_datetime_str, "%Y-%m-%d %H:%M:%S")  #转换为datetime类型
                            if plan_datetime_trans > datetime.now():
                                self.scheduler.add_job(self.schedule_action_datetime, 'date', run_date=plan_datetime_str, kwargs={'id': plan_id, 'action': plan_action})
                                self.PC_data.update_device_service_schedule_next_run_time(self.device_id, plan_id, plan_datetime_str)
                                self.schedule_add_remind_message_job(plan_id, plan_datetime_trans, plan_remind, plan_remind_advance, plan_action)
                        elif plan_type == 'cron':
                            plan_cron = self.PC_funcs.trans_str(plan.get('cron'))
                            minute, hour, day, month, aps_week = self.PC_funcs.trans_cron(plan_cron)
                            trigger = CronTrigger(minute=minute, hour=hour, day=day, month=month, day_of_week=aps_week)
                            next_run = self.schedule_update_next_run_time(plan_id, trigger)
                            next_run_str = str(next_run)
                            self.scheduler.add_job(self.schedule_action_cron, trigger=trigger, kwargs={'id': plan_id, 'trigger': trigger, 'remind': plan_remind, 'advance': plan_remind_advance, 'action': plan_action})
                            self.schedule_add_remind_message_job(plan_id, next_run, plan_remind, plan_remind_advance, plan_action)
                        self.logger.debug(f"已添加定时任务，id：{plan_id}，类型：{plan_type}，下次执行时间：{next_run_str}，操作：{plan_action}")
                    else:
                        self.logger.debug(f"定时任务id：{plan_id}，未启用，跳过")
                except Exception as e:
                    self.logger.error(f"添加定时任务id：{plan_id}，出错：{str(e)}")
                    continue
            self.logger.info("定时开关机任务全部添加完成")
        else:
            self.logger.debug("未启用定时开关机服务，跳过添加定时任务")

    # 定时任务通知提醒
    def schedule_remind_message(self, advance, action, run_time):
        action_dict = {'wol': '开机', 'shutdown': '关机'}
        self.PC_message.send_message(self.device_id, f'将于{advance}分钟后执行:{action_dict.get(action, action)}', desp=f'定时任务提醒，执行时间：{run_time}，执行操作：{action_dict.get(action, action)}')

    # 更新下次执行时间
    def schedule_update_next_run_time(self, id, trigger) -> datetime: 
        # 计算下一次执行时间
        now = datetime.now()
        next_run = trigger.get_next_fire_time(None, now).replace(tzinfo=None)
        self.PC_data.update_device_service_schedule_next_run_time(self.device_id, id, str(next_run))
        self.logger.debug(f"定时任务id：{id}，下次执行时间：" + str(next_run))
        return next_run

    # 添加通知提醒定时器
    def schedule_add_remind_message_job(self, id, next_run:datetime, remind, advance, action):
        # 提前 x 分钟
        if remind:
            remind_message_time = next_run - timedelta(minutes=advance)
            now = datetime.now()
            if remind_message_time > now:
                self.logger.debug(f"定时任务id：{id}，下次通知时间：" + str(remind_message_time))
                self.scheduler.add_job(
                    self.schedule_remind_message,
                    trigger='date',
                    run_date=remind_message_time,
                    args=[advance, action, str(next_run)],
                )
            else:
                self.logger.warning(f"定时任务id：{id}，提醒时间({remind_message_time})早于当前时间({now.strftime('%Y-%m-%d %H:%M:%S')})，跳过本次提醒")

    # 网络唤醒
    def action_wol(self, source='bemfa'):
        src_dict = {'bemfa': 'bemfa', 'schedule': '定时任务'}
        src = src_dict.get(source, source)
        rs = self.PC_funcs.pcwol(self.device_id)
        if rs:
            if 'done' in rs:
                text = f'已发送唤醒指令({src})'
                self.logger.info(text)
                self.PC_message.send_message(self.device_id, text)
            else:
                text = f'发送唤醒指令失败({src})'
                self.logger.error(text + ' → ' + rs)
                self.PC_message.send_message(self.device_id, text)
        else:
            text = f'网络唤醒未启用({src})'
            self.logger.warning(text)
            self.PC_message.send_message(self.device_id, text)

    # 关机
    def action_shutdown(self, source='bemfa'):
        src_dict = {'bemfa': 'bemfa', 'schedule': '定时任务'}
        src = src_dict.get(source, source)
        rs = self.PC_funcs.pcshutdown(self.device_id)
        if rs:
            if 'succeeded' in rs:
                text = f'已发送关机指令({src})'
                self.logger.info(text + ' → ' + rs)
                self.PC_message.send_message(self.device_id, text)
            else:
                text = f'发送关机指令失败({src})'
                self.logger.error(text + ' → ' + rs)
                self.PC_message.send_message(self.device_id, text)
        else:
            text = f'远程关机未启用({src})'
            self.logger.warning(text)
            self.PC_message.send_message(self.device_id, text)

    # 单次定时任务执行操作
    def schedule_action_datetime(self, id, action, source='schedule'):
        if action == 'wol':
            self.action_wol(source)
        elif action == 'shutdown':
            self.action_shutdown(source)
        self.PC_data.update_device_service_schedule_next_run_time(self.device_id, id, '')

    # 循环定时任务执行操作
    def schedule_action_cron(self, id, trigger, remind, advance, action, source='schedule'):
        if action == 'wol':
            self.action_wol(source)
        elif action == 'shutdown':
            self.action_shutdown(source)
        next_run = self.schedule_update_next_run_time(id, trigger)
        self.schedule_add_remind_message_job(id, next_run, remind, advance, action)

    # 统计运行时间
    def get_run_time(self):
        run_timedelta = timedelta(seconds=time.time()-self.start_time)
        # 获取天、小时、分钟和秒
        days = run_timedelta.days
        hours, remainder = divmod(run_timedelta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"已运行：{days}天{hours}小时{minutes}分钟{seconds}秒"

    '''bemfa--------------------------------------------------------'''
    # 订阅
    def connTCP(self):
        while not self.stop_event.is_set():
            try:
                # 创建socket
                self.tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.tcp_client_socket.settimeout(120)
                # 连接服务器
                self.tcp_client_socket.connect((self.server_ip, self.server_port))
                # 发送订阅指令
                substr = f'cmd=1&uid={self.bemfa_uid}&topic={self.bemfa_topic}\r\n'
                self.tcp_client_socket.send(substr.encode('utf-8'))
                # 写入日志
                self.logger.info("bemfa订阅成功")
                break
            except:
                self.logger.error("bemfa订阅失败，1分钟后重试...")
                time.sleep(60)

    # 心跳
    def send_heartbeat_packet(self):
        # 发送心跳
        try:
            self.tcp_client_socket.send('ping\r\n'.encode('utf-8'))
            self.logger.debug("bemfa心跳已发送")
        except:
            self.logger.error("bemfa心跳发送失败")
    
    # 开启定时发送心跳包
    def add_send_heartbeat_packet_job(self):
        try:
            self.scheduler.add_job(self.send_heartbeat_packet, 'interval', seconds=60, next_run_time=datetime.now(), id='send_heartbeat_packet_job')
            self.logger.debug("bemfa心跳服务已启动")
        except Exception as e:
            self.logger.error("bemfa心跳服务启动失败："+str(e))

    # 关闭定时发送心跳包
    def remove_send_heartbeat_packet_job(self):
        if self.scheduler.get_job('send_heartbeat_packet_job'):
            try:
                self.scheduler.remove_job('send_heartbeat_packet_job')
                self.logger.debug("bemfa心跳服务已停止")
            except Exception as e:
                self.logger.error("bemfa心跳服务停止失败："+str(e))

    # 更新巴法云的设备状态
    def update_bemfa(self):
        pc_state = self.PC_data.get_device_status(self.device_id)
        if pc_state:
            if "on" in pc_state or "off" in pc_state:
                try:
                    substr = f'cmd=2&uid={self.bemfa_uid}&topic={self.bemfa_topic}/up&msg={pc_state[1]}\r\n'
                    self.tcp_client_socket.send(substr.encode("utf-8"))
                    self.logger.debug("bemfa云端设备状态更新："+pc_state[0])
                except Exception as e:
                    self.logger.error("bemfa云端设备状态更新失败："+str(e))
    
    # 开启定时更新巴法云的设备状态
    def add_update_bemfa_job(self):
        if self.PC_funcs.checkbool(self.PC_data.get_device_device_ping_enabled(self.device_id)):
            try:
                self.scheduler.add_job(self.update_bemfa, 'interval', seconds=60, next_run_time=datetime.now() + + timedelta(seconds=5), id='update_bemfa_job')
                self.logger.debug("bemfa云端设备状态更新服务已启动")
            except Exception as e:
                self.logger.error("bemfa云端设备状态更新服务启动失败："+str(e))

    # 关闭定时更新巴法云的设备状态
    def remove_update_bemfa_job(self):
        if self.scheduler.get_job('update_bemfa_job'):
            try:
                self.scheduler.remove_job('update_bemfa_job')
                self.logger.debug("bemfa云端设备状态更新服务已停止")
            except Exception as e:
                self.logger.error("bemfa云端设备状态更新服务停止失败："+str(e))

    # 重置重连次数
    def reset_reconnect_count(self):
        self.bemfa_reconnect_count = 0

    # 重置重连次数定时任务
    def add_reset_reconnect_count_job(self):
        self.scheduler.add_job(self.reset_reconnect_count, 'cron', hour=0, minute=0, id='reset_reconnect_count_job')

    # 主循环
    def mainloop(self):
        # 停止信号设置时停止循环
        while not self.stop_event.is_set():
            try:
                # 接收服务器发送过来的数据
                recv_Data = self.tcp_client_socket.recv(1024)
                recv_str = str(recv_Data.decode('utf-8'))
                self.logger.debug(recv_str.replace('\n', '').replace('\r', ''))
            except Exception as e:
                if self.stop_event.is_set():
                    self.logger.debug("bemfa服务已停止")
                else:
                    self.logger.error("接收bemfa服务器消息出错，重新订阅...Error: " + str(e))
                break

            if not recv_Data:
                if self.stop_event.is_set():
                    self.logger.debug("bemfa服务已停止")
                else:
                    self.logger.error("bemfa服务器未返回任何数据，重新订阅...")
                break

            elif f'uid={self.bemfa_uid}' in recv_str:
                # 收到开机消息
                if 'msg=on' in recv_str:
                    self.action_wol()
                # 收到关机消息
                elif 'msg=off' in recv_str:
                    self.action_shutdown()

    # 停止服务
    def stop(self):
        # 如果线程正在运行
        if self.PC_data.get_device_service_thread(self.device_id).is_alive():
            # 如果停止信号未设置
            if not self.stop_event.is_set():
                # 设置停止信号
                self.stop_event.set()
                # 关闭定时器
                self.scheduler.shutdown(wait=False)
                # 如果巴法服务已启用
                if self.bemfa_enabled:
                    # 关闭连接
                    try:
                        self.tcp_client_socket.shutdown(socket.SHUT_RDWR)
                    except Exception as e:
                        self.logger.debug("shutdown socket error："+str(e))
                    try:
                        self.tcp_client_socket.close()
                    except Exception as e:
                        self.logger.debug("close socket error："+str(e))
                    self.logger.debug("bemfa服务已停止")
                # 删除设备状态记录
                self.PC_data.delete_device_status(self.device_id)
                self.PC_data.delete_device_service_schedule(self.device_id)
                self.logger.info(f"设备{self.device_id}所有服务已停止")
                # 删除日志记录器
                self.PC_log.remove_logger(self.logger_name)
                # 已停止符号
                self.stopped = True

    # 启动准备
    def start(self, stop_event):
        # 检查是否启动设备服务
        self.enabled = self.PC_funcs.checkbool(self.PC_data.get_device_main_enabled(self.device_id))
        # 如果启用
        if self.enabled:
            # 启动时间
            self.start_time = time.time()
            # 全局日志等级
            self.logger_level = self.PC_data.get_main_yaml_log_level()
            # 生成日志记录器
            self.set_logger()
            # 生成定时器
            self.scheduler = BackgroundScheduler()
            # 开启定时器
            self.scheduler.start()
            # 停止符号
            self.stopped = False
            # 停止信号
            self.stop_event = stop_event
            self.is_power_off = False
            self.bemfa_enabled = self.PC_funcs.checkbool(self.PC_data.get_device_bemfa_enabled(self.device_id))
            if self.bemfa_enabled:
                self.bemfa_uid = self.PC_data.get_device_bemfa_uid(self.device_id)
                self.bemfa_topic = self.PC_data.get_device_bemfa_topic(self.device_id)
                self.bemfa_reconnect_count = 0
            self.run()
        else:
            self.PC_logger.warning(f"{self.device_id}服务未启用")

    # 启动
    def run(self):
        self.logger.info(f"设备{self.device_id}服务启动")
        retry = False
        # 开启ping服务
        self.add_ping_job()
        # 检查停止符号，所有服务都停止则退出循环关闭线程
        while not self.stopped:
            # 检查停止信号，如果停止则循环1s检查是否已停止所有服务
            while not self.stop_event.is_set():
                if self.bemfa_enabled:
                    # 如果不是重连（第一次连接）
                    if not retry:
                        self.logger.info("bemfa服务启动")
                        self.add_reset_reconnect_count_job()
                        self.schedule_add_plans_job()
                    # 如果是重连
                    elif retry:
                        # 重连次数+1
                        self.bemfa_reconnect_count += 1
                        self.logger.warning(f"正在重新订阅bemfa(今日第{self.bemfa_reconnect_count}次)")
                        # 先移除定时任务
                        self.remove_send_heartbeat_packet_job()
                        self.remove_update_bemfa_job()
                        # 如果开启了巴法重连消息推送
                        if self.PC_data.get_main_yaml_message_bemfa_reconnect():
                            self.PC_message.send_message('main', f'重新订阅bemfa提醒', desp=f'正在重新订阅bemfa\n\n断连时间：{self.PC_funcs.get_time()}\n\n可能的原因：网络发生短暂断开；bemfa服务器偶然断连。\n\n*当天重连推送达5次后将不再推送，请查看日志。', type='bemfa_reconnect')
                        try:
                            self.tcp_client_socket.close()
                        except Exception as e:
                            self.logger.error("关闭TCP连接失败，Error: " + str(e))
                        if self.bemfa_reconnect_count > 5:
                            if self.bemfa_reconnect_count == 6:
                                self.logger.warning("今日重连已达5次，后续重连将有60秒的等待时间")
                            self.logger.info("等待60秒重连bemfa...")
                            time.sleep(60)
                    self.connTCP()
                    self.add_send_heartbeat_packet_job()
                    self.add_update_bemfa_job()
                    self.mainloop()
                    retry=True
                else:
                    # 巴法服务未启用的情况下维持线程运行，确保ping服务正常运行
                    self.stop_event.wait(timeout=3600)
            time.sleep(1)