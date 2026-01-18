// config-device.html
document.addEventListener("touchstart", function () { }, true);

// 获取当前页面的 URL
let currentUrl = new URL(window.location.href);
// 获取 URL 中的 key 参数
let KEY = currentUrl.searchParams.get('key');

// ----------------------------------------------------------------------------------------------------
// 顶部模糊效果
window.addEventListener('DOMContentLoaded', checkBlur);
window.addEventListener('resize', checkBlur);
document.querySelector('.head-container').addEventListener('scroll', checkBlur);

function checkBlur() {
    const headContainer = document.querySelector('.head-container');
    const blurLeft = document.querySelector('.blur-left');
    const blurRight = document.querySelector('.blur-right');

    if (!headContainer || !blurLeft || !blurRight) return;

    // 检查左侧是否有可滑动元素
    if (headContainer.scrollLeft > 0) {
        blurLeft.style.opacity = 1; // 显示左侧模糊提示
    } else {
        blurLeft.style.opacity = 0; // 隐藏左侧模糊提示
    }

    // 检查右侧是否有可滑动元素
    if (headContainer.scrollLeft < headContainer.scrollWidth - headContainer.clientWidth) {
        blurRight.style.opacity = 1; // 显示右侧模糊提示
    } else {
        blurRight.style.opacity = 0; // 隐藏右侧模糊提示
    }
}
// ----------------------------------------------------------------------------------------------------
// 设置跳转url
document.getElementById('main').href = `/config?key=${KEY}`;
document.getElementById('logs').href = `/logs?key=${KEY}`;
document.getElementById('go_wol').href = `/wol/${DEVICE_ID}?key=${KEY}`;
document.getElementById('go_shutdown').href = `/shutdown/${DEVICE_ID}?key=${KEY}`;
document.getElementById('go_ping').href = `/ping/${DEVICE_ID}?key=${KEY}`;

// ----------------------------------------------------------------------------------------------------
// 消息显示
function addFlashMessage(content) {
    const now = new Date();
    const timestamp = now.toLocaleString('zh-CN', { hour12: false })
        .replace(/\//g, '-')
        .replace(',', ''); // 格式: YYYY-MM-DD HH:MM:SS
    const flashMessages = document.getElementById('flash-messages');
    // 清空之前的内容
    // flashMessages.innerHTML = "";
    const messageElement = document.createElement('ul');
    const messageItem = document.createElement('li');
    messageItem.innerHTML = `${timestamp}<br>${content}`;
    messageElement.appendChild(messageItem);
    flashMessages.appendChild(messageElement);
}

// ----------------------------------------------------------------------------------------------------
// 按钮功能
// 刷新延时
let ReloadDelayTime = 3000;
// 启动按钮
function sendStartRequest() {
    window.scrollTo({ top: 0 });
    addFlashMessage("正在启动服务，请稍候...");
    // 使用 Fetch API 发送 POST 请求
    fetch(`/device/start/${DEVICE_ID}?key=${KEY}`, { method: 'POST' })
        .then(response => {
            if (!response.ok) addFlashMessage("请求失败：" + response.status);
            return response.json();
        })
        .then(data => {
            if (data.result) {
                addFlashMessage("启动完成，页面即将刷新")
                setTimeout(function () {
                    location.reload(); // 刷新页面
                }, ReloadDelayTime);
            } else {
                addFlashMessage("启动出现问题，请查看日志")
            }
        })
};
// 停止按钮
function sendStopRequest() {
    window.scrollTo({ top: 0 });
    addFlashMessage("正在停止服务，请稍候...");
    // 使用 Fetch API 发送 POST 请求
    fetch(`/device/stop/${DEVICE_ID}?key=${KEY}`, { method: 'POST' })
        .then(response => {
            if (!response.ok) addFlashMessage("请求失败：" + response.status);
            return response.json();
        })
        .then(data => {
            if (data.result) {
                addFlashMessage("停止完成，页面即将刷新")
                setTimeout(function () {
                    location.reload(); // 刷新页面
                }, ReloadDelayTime);
            } else {
                addFlashMessage("停止出现问题，请查看日志")
            }
        })
};
// 重启按钮
function sendRestartRequest() {
    window.scrollTo({ top: 0 });
    addFlashMessage("正在重启服务，请稍候...");
    // 使用 Fetch API 发送 POST 请求
    fetch(`/device/restart/${DEVICE_ID}?key=${KEY}`, { method: 'POST' })
        .then(response => {
            if (!response.ok) addFlashMessage("请求失败：" + response.status);
            return response.json();
        })
        .then(data => {
            if (data.result) {
                addFlashMessage("重启完成，页面即将刷新")
                setTimeout(function () {
                    location.reload(); // 刷新页面
                }, ReloadDelayTime);
            } else {
                addFlashMessage("重启出现问题，请查看日志")
            }
        })
};
// 删除按钮
function sendDeleteRequest() {
    // 弹窗确认
    swal({
        title: "确定要删除该设备服务吗？",
        buttons: ["取消", "确定删除"],
        dangerMode: true,
    }).then((willDelete) => {
        if (!willDelete) return;
        window.scrollTo({ top: 0 });
        addFlashMessage("正在删除设备服务，请稍候...");
        // 使用 Fetch API 发送 POST 请求
        fetch(`/device/delete/${DEVICE_ID}?key=${KEY}`, { method: 'DELETE' })
            .then(response => {
                if (!response.ok) addFlashMessage("请求失败：" + response.status);
                return response.json();
            })
            .then(data => {
                if (data.result) {
                    addFlashMessage("已删除，即将返回总览")
                    setTimeout(function () {
                        window.location.href = `/config?key=${KEY}`;
                    }, ReloadDelayTime);
                } else {
                    addFlashMessage("删除出现问题，请查看日志")
                }
            })
    });
};
document.getElementById('start_top_btn').addEventListener('click', sendStartRequest);
document.getElementById('start_bottom_btn').addEventListener('click', sendStartRequest);
document.getElementById('stop_top_btn').addEventListener('click', sendStopRequest);
document.getElementById('stop_bottom_btn').addEventListener('click', sendStopRequest);
document.getElementById('restart_top_btn').addEventListener('click', sendRestartRequest);
document.getElementById('restart_bottom_btn').addEventListener('click', sendRestartRequest);
document.getElementById('delete_top_btn').addEventListener('click', sendDeleteRequest);
document.getElementById('delete_bottom_btn').addEventListener('click', sendDeleteRequest);

// ----------------------------------------------------------------------------------------------------
// 根据复选框状态更新跳转链接的显示或隐藏
function go_func_show() {
    const items = [
        'bemfa', 'wol', 'shutdown', 'ping'
    ];

    items.forEach(item => {
        const enabled_id = `${item}_enabled`;
        const go_id = `go_${item}`;

        const goElement = document.getElementById(go_id);

        // 根据 enabled 元素的 checked 属性值，添加或移除 visible 类
        if (document.getElementById(enabled_id).checked) {
            goElement.classList.remove('hidden');
            goElement.classList.add('visible');
        } else {
            goElement.classList.remove('visible');
            goElement.classList.add('hidden');
        }
    });
}

// 根据复选框状态更新对应内容的显示或隐藏
function ifshow(event) {
    const checkbox = event.target; // 当前触发事件的复选框
    const targetId = checkbox.dataset.target; // 获取对应的内容 ID
    const targetElement = document.getElementById(targetId); // 获取目标内容元素

    if (checkbox.checked) {
        targetElement.classList.remove('hidden');
        targetElement.classList.add('visible');
    } else {
        targetElement.classList.remove('visible');
        targetElement.classList.add('hidden');
    }
    go_func_show();
}

// 页面加载完成后为所有复选框添加事件监听
document.addEventListener('DOMContentLoaded', () => {
    const checkboxes = document.querySelectorAll(
        '.checkbox-label:not(#main_enabled):not(#push_enabled):not(.schedule-enabled):not(.schedule-remind)'
    );

    checkboxes.forEach(checkbox => {
        // 初始化显示状态
        const targetId = checkbox.dataset.target;
        const targetElement = document.getElementById(targetId);

        if (checkbox.checked) {
            targetElement.classList.remove('hidden');
        } else {
            targetElement.classList.add('hidden');
        }
        go_func_show()
        // 添加监听事件
        checkbox.addEventListener('change', ifshow);
    });

    // 初始化 schedule 编辑区
    initScheduleEditor();
});

// ----------------------------------------------------------------------------------------------------
// schedule 编辑
function initScheduleEditor() {
    const scheduleList = document.getElementById('schedule_list');
    const addBtn = document.getElementById('add_schedule_plan_btn');
    const hiddenInput = document.getElementById('schedule_plans_input');
    // 确保后端能收到 schedule.plans
    if (hiddenInput) {
        hiddenInput.setAttribute('name', 'schedule.plans');
    }

    function serializePlans() {
        const plans = [];
        document.querySelectorAll('.schedule-plan').forEach(planEl => {
            const id = planEl.querySelector('.schedule-id').value;
            const enabled = planEl.querySelector('.schedule-enabled').checked;
            const name = planEl.querySelector('.schedule-name').value;
            const type = planEl.querySelector('.schedule-type').value;
            let datetime = planEl.querySelector('.schedule-datetime').value;
            // datetime-local → 'YYYY-M-D HH:MM:SS'
            if (datetime && datetime.includes('T')) {
                datetime = datetime.replace('T', ' ');
                if (datetime.length === 16) {
                    datetime += ':00';
                }
            }
            const cron = planEl.querySelector('.schedule-cron').value;
            const action = planEl.querySelector('.schedule-action').value;
            const remind = planEl.querySelector('.schedule-remind').checked;
            const advance = parseInt(planEl.querySelector('.schedule-advance').value) || 5;
            plans.push({ id, enabled, name, type, datetime, cron, action, remind, advance });
        });
        hiddenInput.value = JSON.stringify(plans);
    }

    function removePlan(e) {
        const planEl = e.target.closest('.schedule-plan');
        if (!planEl) return;
        planEl.remove();
        serializePlans();
    }

    function addPlanWithData(data) {
        const idx = document.querySelectorAll('.schedule-plan').length;
        const div = document.createElement('div');
        // 标记为 schedule-plan
        div.classList.add('schedule-hr', 'schedule-plan');
        div.dataset.index = idx;
        div.innerHTML = `
            id： <input class="input-label schedule-id" type="text" value="${data.id || ''}" readonly><br>
            名称： <input class="input-label schedule-name" type="text" value="${data.name || ''}" placeholder="名称">
            <span class="tooltip no-select">❔︎
                <span class="tooltiptext">随便更改，如：每周六晚11点关机</span>
            </span><br>
            启用：
            <input id="schedule_enabled_${idx}" class="checkbox-label schedule-enabled" type="checkbox" ${data.enabled ? 'checked' : ''} data-target="schedule_body_${idx}">
            <label for="schedule_enabled_${idx}" style="margin-bottom: 6px;"></label>
            <br>
            <div id="schedule_body_${idx}" class="schedule-body${!data.enabled ? ' hidden' : ''}">
                类型：
                <select class="input-label schedule-type">
                    <option value="datetime" ${data.type == 'datetime' ? 'selected' : ''}>单次</option>
                    <option value="cron" ${data.type == 'cron' ? 'selected' : ''}>循环</option>
                </select>
                <br>
                <div class="schedule-datetime-wrapper${data.type !== 'datetime' ? ' hidden' : ''}">
                    时间：
                    <input class="datetime-label schedule-datetime" style="width: 260px;" 
                        type="datetime-local"
                        step="1"
                        value="${data.datetime ? data.datetime.replace(' ', 'T') : ''}">
                    <br>
                </div>
                <div class="schedule-cron-wrapper${data.type !== 'cron' ? ' hidden' : ''}">
                    cron表达式：
                    <input class="input-label schedule-cron" type="text" value="${data.cron || '* * * * *'}" placeholder="* * * * *">
                    <span class="tooltip no-select">❔︎
                        <span class="tooltiptext">格式为5段cron表达式,数字,不支持英文。tips:可借助AI快速生成</span>
                    </span><br>
                    <a style="font-size:14px;color: #4CAF50;"> ➔快速生成cron表达式：</a>
                    <a class="textlink" href="/getcron" target="_blank">本地版</a>
                    <a class="textlink" href="https://tool.hoothin.com/zh-CN/cron-parser-generator" target="_blank">在线版</a>
                    <br>
                </div>
                操作：<select class="input-label schedule-action">
                        <option value="wol" ${data.action == 'wol' ? 'selected' : ''}>开机</option>
                        <option value="shutdown" ${data.action == 'shutdown' ? 'selected' : ''}>关机</option>
                    </select><br>
                下次执行时间：<span class="schedule-next-runtime">无</span>
                            <span class="tooltip no-select">❔︎
                                <span class="tooltiptext">保存并重启服务后更新下次执行时间</span>
                            </span><br>
                提前推送提醒：
                <input id="schedule_remind_${idx}" class="checkbox-label schedule-remind" type="checkbox" ${data.remind ? 'checked' : ''} data-target="">
                <label for="schedule_remind_${idx}" style="margin-bottom: 6px;"></label>
                <span class="tooltip no-select">❔︎
                    <span class="tooltiptext">需同时勾选主程序和单个设备的消息推送开关</span>
                </span>
                <br>
                <div class="schedule-advance-wrapper${!data.remind ? ' hidden' : ''}">
                    提前时间(分钟)：
                    <input class="input-label schedule-advance" type="number" value="${data.advance || 5}" min="1"><br>
                </div>
            </div>
            <button type="button" style="background-color: rgb(255, 102, 102); margin-bottom: 10px;" class="remove-plan-btn">删除</button>
        `;
        scheduleList.appendChild(div);
        div.querySelector('.remove-plan-btn').addEventListener('click', removePlan);
        // 监听所有输入变化自动序列化
        div.querySelectorAll('input,select').forEach(el => el.addEventListener('change', serializePlans));

        // 定时任务启用勾选显示/隐藏
        const enabledCb = div.querySelector('.schedule-enabled');
        const body = div.querySelector(`#schedule_body_${idx}`);

        enabledCb.addEventListener('change', () => {
            if (enabledCb.checked) {
                body.classList.remove('hidden');
                body.classList.add('visible');
            } else {
                body.classList.remove('visible');
                body.classList.add('hidden');
            }
            serializePlans();
        });

        // 类型切换显示/隐藏
        const typeSelect = div.querySelector('.schedule-type');
        const dtWrap = div.querySelector('.schedule-datetime-wrapper');
        const cronWrap = div.querySelector('.schedule-cron-wrapper');

        function updateType() {
            const isDatetime = typeSelect.value === 'datetime';
            if (isDatetime) {
                dtWrap.classList.remove('hidden');
                dtWrap.classList.add('visible');
                cronWrap.classList.remove('visible');
                cronWrap.classList.add('hidden');
            } else {
                dtWrap.classList.remove('visible');
                dtWrap.classList.add('hidden');
                cronWrap.classList.remove('hidden');
                cronWrap.classList.add('visible');
            }
            serializePlans();
        }
        typeSelect.addEventListener('change', updateType);
        updateType();

        // 提醒勾选显示/隐藏
        const remindCb = div.querySelector('.schedule-remind');
        const advWrap = div.querySelector('.schedule-advance-wrapper');

        remindCb.addEventListener('change', () => {
            if (remindCb.checked) {
                advWrap.classList.remove('hidden');
                advWrap.classList.add('visible');
            } else {
                advWrap.classList.remove('visible');
                advWrap.classList.add('hidden');
            }
            serializePlans();
        });

        // tooltip 点击显示/隐藏
        div.querySelectorAll('.tooltip').forEach(el => {
            el.addEventListener('click', function (event) {
                event.stopPropagation(); // 阻止冒泡，防止触发 document 点击隐藏
                this.classList.toggle('show');
            });
        });

        serializePlans();
    }

    addBtn.addEventListener('click', function () {
        addPlanWithData({
            id: Math.floor(Date.now() / 1000).toString(),
            enabled: false,
            name: '新建任务',
            type: 'cron',
            datetime: '',
            cron: '* * * * *',
            action: 'shutdown',
            remind: false,
            advance: 5
        });
    });

    // 为已有的删除按钮绑定事件（如果页面渲染已有节点）
    document.querySelectorAll('.schedule-plan .remove-plan-btn').forEach(btn => btn.addEventListener('click', removePlan));
    // 初始序列化一次
    serializePlans();
    // 提交表单前，确保 schedule 数据已最新序列化
    const form = document.getElementById('pcconfig');
    if (form) {
        form.addEventListener('submit', function () {
            serializePlans();
        });
    }

    // 已存在任务初始化逻辑
    document.querySelectorAll('.schedule-plan').forEach(planEl => {
        const enabledCb = planEl.querySelector('.schedule-enabled');
        const body = planEl.querySelector('[id^="schedule_body_"]');
        if (enabledCb && body) {
            if (enabledCb.checked) {
                body.classList.remove('hidden');
                body.classList.add('visible');
            } else {
                body.classList.remove('visible');
                body.classList.add('hidden');
            }
            enabledCb.addEventListener('change', () => {
                if (enabledCb.checked) {
                    body.classList.remove('hidden');
                    body.classList.add('visible');
                } else {
                    body.classList.remove('visible');
                    body.classList.add('hidden');
                }
                serializePlans();
            });
        }

        const typeSelect = planEl.querySelector('.schedule-type');
        const dtWrap = planEl.querySelector('.schedule-datetime-wrapper');
        const cronWrap = planEl.querySelector('.schedule-cron-wrapper');
        if (typeSelect && dtWrap && cronWrap) {
            const updateType = () => {
                const isDatetime = typeSelect.value === 'datetime';
                if (isDatetime) {
                    dtWrap.classList.remove('hidden');
                    dtWrap.classList.add('visible');
                    cronWrap.classList.remove('visible');
                    cronWrap.classList.add('hidden');
                } else {
                    dtWrap.classList.remove('visible');
                    dtWrap.classList.add('hidden');
                    cronWrap.classList.remove('hidden');
                    cronWrap.classList.add('visible');
                }
                serializePlans();
            };
            typeSelect.addEventListener('change', updateType);
            updateType();
        }

        const remindCb = planEl.querySelector('.schedule-remind');
        const advWrap = planEl.querySelector('.schedule-advance-wrapper');
        if (remindCb && advWrap) {
            if (remindCb.checked) {
                advWrap.classList.remove('hidden');
                advWrap.classList.add('visible');
            } else {
                advWrap.classList.remove('visible');
                advWrap.classList.add('hidden');
            }
            remindCb.addEventListener('change', () => {
                if (remindCb.checked) {
                    advWrap.classList.remove('hidden');
                    advWrap.classList.add('visible');
                } else {
                    advWrap.classList.remove('visible');
                    advWrap.classList.add('hidden');
                }
                serializePlans();
            });
        }
    });
}

// ----------------------------------------------------------------------------------------------------
// 隐藏or显示元素
function showElement(element) {
    element.classList.remove('hidden');
    element.classList.add('visible');
}

function hideElement(element) {
    element.classList.remove('visible');
    element.classList.add('hidden');
}

// ----------------------------------------------------------------------------------------------------
// 下拉框选择事件
// wol
// 获取元素
const wolMethodSelect = document.getElementById('wol_method');
const wakeonlanConfig = document.getElementById('wakeonlanconfig');
const wol_shell_script = document.getElementById('wol_shell_script');

// 更新显示状态
function ifshow_method_wol() {

    hideElement(wakeonlanConfig);
    hideElement(wol_shell_script);

    if (wolMethodSelect.value === 'wakeonlan') {
        showElement(wakeonlanConfig);
    } else if (wolMethodSelect.value === 'shell') {
        showElement(wol_shell_script);
    }
}

// 监听
function handleSelectChangeWol() {
    ifshow_method_wol();
}

// shutdown
// 获取元素
const shutdownMethodSelect = document.getElementById('shutdown_method');
const netrpcConfig = document.getElementById('netrpcconfig');
const udpconfig = document.getElementById('udpconfig');
const shutdown_shell_script = document.getElementById('shutdown_shell_script');
const shutdown_delay_time = document.getElementById('shutdown_delay_time');

// 更新显示状态
function ifshow_method_shutdown() {
    hideElement(netrpcConfig);
    hideElement(udpconfig);
    hideElement(shutdown_shell_script);
    hideElement(shutdown_delay_time);

    if (shutdownMethodSelect.value === 'netrpc') {
        showElement(netrpcConfig);
        showElement(shutdown_delay_time);
    } else if (shutdownMethodSelect.value === 'udp') {
        showElement(udpconfig);
        showElement(shutdown_delay_time);
    } else if (shutdownMethodSelect.value === 'shell') {
        showElement(shutdown_shell_script);
    }
}

// 监听
function handleSelectChangeShutdown() {
    ifshow_method_shutdown();
}

// ping
// 获取元素
const pingMethodSelect = document.getElementById('ping_method');
const ping_shell_script = document.getElementById('ping_shell_script');

// 更新显示状态
function ifshow_method_ping() {

    hideElement(ping_shell_script);

    if (pingMethodSelect.value === 'shell') {
        showElement(ping_shell_script);
    }
}

// 监听
function handleSelectChangePing() {
    ifshow_method_ping();
}

// 页面加载初始调用
document.addEventListener('DOMContentLoaded', () => {
    ifshow_method_wol();
    ifshow_method_shutdown();
    ifshow_method_ping();

    // 监听select的change事件
    wolMethodSelect.addEventListener('change', handleSelectChangeWol);
    shutdownMethodSelect.addEventListener('change', handleSelectChangeShutdown);
    pingMethodSelect.addEventListener('change', handleSelectChangePing);
});

// ----------------------------------------------------------------------------------------------------
// 另一个保存按钮功能
function submit_pcconfig() {
    document.getElementById("pcconfig").submit();
}

// ----------------------------------------------------------------------------------------------------
// 动态调整输入框宽度
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".input-label").forEach((input) => {
        // 默认宽度
        const defaultWidth = window.getComputedStyle(input).width;

        function adjustWidth() {
            // 创建一个临时span元素来计算文本长度
            let tempSpan = document.createElement("span");
            tempSpan.style.visibility = "hidden";
            tempSpan.style.position = "absolute"; // 避免影响布局
            tempSpan.style.whiteSpace = "nowrap"; // 确保单行计算宽度
            tempSpan.style.fontSize = window.getComputedStyle(input).fontSize;
            tempSpan.style.fontFamily = window.getComputedStyle(input).fontFamily;
            tempSpan.innerText = input.value || input.placeholder || "输入文本";
            document.body.appendChild(tempSpan);

            // 计算并设置input宽度
            input.style.width = `${tempSpan.offsetWidth + 20}px`;

            document.body.removeChild(tempSpan);
        }

        // 监听用户输入或粘贴
        input.addEventListener("input", adjustWidth);
        // 监听焦点事件来调整宽度
        input.addEventListener("focus", adjustWidth);
        // 失去焦点时恢复默认宽度
        input.addEventListener("blur", function () {
            input.style.width = defaultWidth;;
        });
    });
});

// ----------------------------------------------------------------------------------------------------
// 下载确认
function confirmDownload() {
    var result = confirm("确认下载");
    return result;
}

// ----------------------------------------------------------------------------------------------------
// 实时更新wol目标地址
function update_wol_dest() {
    const ipInput = document.getElementById('device_ip').value;
    const broadcastIpDirect = document.getElementById('broadcast_ip_direct');
    const broadcastDeviceIp = document.getElementById('broadcast_device_ip');

    // 更新定向广播选项
    const broadcastIp = ipInput.slice(0, ipInput.lastIndexOf('.') + 1) + '255';
    broadcastIpDirect.textContent = '定向广播(' + broadcastIp + ')';

    // 更新设备IP选项
    broadcastDeviceIp.textContent = '设备ip(' + ipInput + ')';
}

// 页面加载时更新
window.onload = update_wol_dest;

// ----------------------------------------------------------------------------------------------------
// 提示信息
// 点击 ❔︎ 显示/隐藏（适合手机触屏）
document.querySelectorAll('.tooltip').forEach(el => {
    el.addEventListener('click', function (event) {
        event.stopPropagation(); // 阻止冒泡，防止触发 document 点击隐藏
        this.classList.toggle('show');
    });
});

// 点击页面空白处隐藏 tooltip
document.addEventListener('click', function () {
    document.querySelectorAll('.tooltip').forEach(el => {
        el.classList.remove('show');
    });
});