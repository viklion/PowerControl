// overview.html

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

// ----------------------------------------------------------------------------------------------------
// 消息显示
function addFlashMessage(content) {
    const now = new Date();
    const timestamp = now.toISOString().slice(0, 19).replace("T", " "); // 格式: YYYY-MM-DD HH:MM:SS
    const flashMessages = document.getElementById('flash-messages');
    // 清空之前的内容
    flashMessages.innerHTML = "";
    const messageElement = document.createElement('ul');
    const messageItem = document.createElement('li');
    messageItem.innerHTML = `${timestamp}<br>${content}`;
    messageElement.appendChild(messageItem);
    flashMessages.appendChild(messageElement);
}

// ----------------------------------------------------------------------------------------------------
// 按钮功能
// 新建设备按钮
function sendNewDeviceRequest() {
    window.scrollTo({ top: 0 });
    addFlashMessage("正在新建设备服务，请稍候...");
    // 使用 Fetch API 发送 POST 请求
    fetch(`/device/new?key=${KEY}`, { method: 'POST' })
        .then(response => {
            if (!response.ok) addFlashMessage("请求失败：" + response.status);
            return response.json();
        })
        .then(data => {
            if (data.result) {
                addFlashMessage("新建设备服务完成")
                fetchAllDevicesBrief();
            } else {
                addFlashMessage("新建设备服务出现问题，请查看日志")
            }
        })
};
// 启动全部按钮
function sendStartAllRequest() {
    // 弹窗确认
    if (!confirm("确定要启动全部服务吗？")) {
        return; // 用户取消，直接返回
    }
    window.scrollTo({ top: 0 });
    addFlashMessage("正在启动全部服务，请稍候...");
    // 使用 Fetch API 发送 POST 请求
    fetch(`/device/start/all?key=${KEY}`, { method: 'POST' })
        .then(response => {
            if (!response.ok) addFlashMessage("请求失败：" + response.status);
            return response.json();
        })
        .then(data => {
            if (data.result) {
                addFlashMessage("启动全部服务完成")
                fetchAllDevicesBrief();
            } else {
                addFlashMessage("启动全部服务出现问题，请查看日志")
            }
        })
};
// 停止全部按钮
function sendStopAllRequest() {
    // 弹窗确认
    if (!confirm("确定要停止全部服务吗？")) {
        return; // 用户取消，直接返回
    }
    window.scrollTo({ top: 0 });
    addFlashMessage("正在停止全部服务，请稍候...");
    // 使用 Fetch API 发送 POST 请求
    fetch(`/device/stop/all?key=${KEY}`, { method: 'POST' })
        .then(response => {
            if (!response.ok) addFlashMessage("请求失败：" + response.status);
            return response.json();
        })
        .then(data => {
            if (data.result) {
                addFlashMessage("停止全部服务完成")
                fetchAllDevicesBrief();
            } else {
                addFlashMessage("停止全部服务出现问题，请查看日志")
            }
        })
};
// 重启全部按钮
function sendRestartAllRequest() {
    // 弹窗确认
    if (!confirm("确定要重启全部服务吗？")) {
        return; // 用户取消，直接返回
    }
    window.scrollTo({ top: 0 });
    addFlashMessage("正在重启全部服务，请稍候...");
    // 使用 Fetch API 发送 POST 请求
    fetch(`/device/restart/all?key=${KEY}`, { method: 'POST' })
        .then(response => {
            if (!response.ok) addFlashMessage("请求失败：" + response.status);
            return response.json();
        })
        .then(data => {
            if (data.result) {
                addFlashMessage("重启全部服务完成")
                fetchAllDevicesBrief();
            } else {
                addFlashMessage("重启全部服务出现问题，请查看日志")
            }
        })
};
// 重启容器按钮
function sendRestartContainerRequest() {
    // 弹窗确认
    if (!confirm("确定要重启容器吗？")) {
        return; // 用户取消，直接返回
    }
    window.scrollTo({ top: 0 });
    // 使用 Fetch API 发送 POST 请求
    fetch(`/restart?key=${KEY}`, { method: 'POST' })
    // 初始化倒计时
    let countdown = 5;
    addFlashMessage(`即将于${countdown}s后刷新`)
        
    // 设置定时器每秒更新一次消息
    const intervalId = setInterval(function () {
        countdown--;

        // 倒计时结束后刷新页面
        if (countdown < 1) {
            clearInterval(intervalId); // 清除定时器
            location.reload(); // 刷新页面
        }
    }, 1000); // 每隔1秒更新一次 
};

document.getElementById('new_device_top_btn').addEventListener('click', sendNewDeviceRequest);
document.getElementById('start_all_top_btn').addEventListener('click', sendStartAllRequest);
document.getElementById('stop_all_top_btn').addEventListener('click', sendStopAllRequest);
document.getElementById('restart_all_top_btn').addEventListener('click', sendRestartAllRequest);
document.getElementById('restart_container_top_btn').addEventListener('click', sendRestartContainerRequest);

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

// ----------------------------------------------------------------------------------------------------
// 设备信息卡片
const container = document.getElementById('deviceContainer');

function fetchAllDevicesBrief() {
    fetch(`/device/get/all-brief?key=${KEY}`)
        .then(resp => resp.json())
        .then(data => {
            container.innerHTML = '';
            Object.entries(data).forEach(([deviceId, info]) => {
                const card = document.createElement('div');
                card.className = 'device-card';

                // 点击跳转设备编辑页
                card.onclick = () => {
                    window.open(`/config/${deviceId}?key=${KEY}`, '_blank');
                };

                if (deviceId === 'main') {
                    const messageEnabledText = info.message_enabled ? '启用' : '未启用'; 
                    const messageEnabledClass = info.message_enabled ? 'status-on' : 'status-off';
                    card.innerHTML = `
                            <h3>主程序</h3>
                            <p><strong>设备ID：</strong> ${deviceId}</p>
                            <p><strong>日志等级：</strong> ${info.log_level}</p>
                            <p><strong>日志保留天数：</strong> ${info.log_days}</p>
                            <p><strong>消息推送：</strong> <span class="${messageEnabledClass}">${messageEnabledText}</span></p>
                        `;
                } else {
                    const aliasText = info.alias ? info.alias : '未设置';
                    // 设备状态显示
                    const statusText = info.status && info.status[0] ? info.status[0] : '未知';
                    const statusClass = info.status && info.status[1] === 'on' ? 'status-on' :
                        info.status && info.status[1] === 'off' ? 'status-off' :
                            'status-unknown';

                    // 运行状态
                    const runningText = info.running ? '运行中' : '未运行';
                    const enabledText = info.enabled ? '启用' : '未启用';
                    const runningClass = info.running ? 'status-on' : 'status-off';
                    const enabledClass = info.enabled ? 'status-on' : 'status-off';

                    card.innerHTML = `
                        <div class="card-header">
                            <h3>${info.name}</h3>
                            <div class="card-actions">
                                <button class="action-btn power-on" title="开机" dev-id="${deviceId}">ON</button>
                                <button class="action-btn power-off" title="关机" dev-id="${deviceId}">OFF</button>
                            </div>
                        </div>
                        <p><strong>启用：</strong> <span class="${enabledClass}">${enabledText}</span></p>
                        <p><strong>设备ID：</strong> ${deviceId}</p>
                        <p><strong>api别名：</strong> ${aliasText}</p>
                        <p><strong>状态：</strong> <span class="${statusClass}">${statusText}</span></p>
                        <p><strong>IP：</strong> ${info.ip || '-'}</p>
                        <p><strong>服务：</strong> <span class="${runningClass}">${runningText}</span></p>
                    `;
                }
                container.appendChild(card);
            });
            // 给按钮绑定点击事件
            container.querySelectorAll('.power-on').forEach(btn => {
                btn.addEventListener('click', e => {
                    e.stopPropagation(); // 阻止触发 card.onclick
                    if (!confirm("确认开机？")) {
                        return;
                    }
                    const id = btn.getAttribute('dev-id');
                    window.open(`/wol/${id}?key=${KEY}`, '_blank');
                });
            });
            container.querySelectorAll('.power-off').forEach(btn => {
                btn.addEventListener('click', e => {
                    e.stopPropagation();
                    if (!confirm("确认关机？")) {
                        return;
                    }
                    const id = btn.getAttribute('dev-id');
                    window.open(`/shutdown/${id}?key=${KEY}`, '_blank');
                });
            });
        })
        .catch(err => {
            container.innerHTML = '<p>无法加载设备信息，请检查网络或刷新页面。</p>';
            console.error(err);
        });
};

// 页面加载调用
window.addEventListener('DOMContentLoaded', () => {
    fetchAllDevicesBrief();
});

// 每 x 秒调用一次
setInterval(fetchAllDevicesBrief, 5000);