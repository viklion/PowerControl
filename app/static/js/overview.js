// overview.html
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

// ----------------------------------------------------------------------------------------------------
// 消息显示
function addFlashMessage(content) {
    const now = new Date();
    const timestamp = now.toLocaleString('zh-CN', { hour12: false })
        .replace(/\//g, '-')
        .replace(',', ''); // 格式: YYYY-MM-DD HH:MM:SS
    const flashMessages = document.getElementById('flash-messages');
    // 清空之前的内容
    flashMessages.innerHTML = "";
    const messageElement = document.createElement('ul');
    const messageItem = document.createElement('li');
    messageItem.innerHTML = `${timestamp}<br>${content.replace(/\n/g, '<br>')}`;
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
// 全部开机按钮
function sendWolAllRequest() {
    swal({
        title: "确定要全部开机吗？",
        text: "将唤醒所有设备！",
        icon: "warning",
        buttons: ["取消", "确定开机"],
        dangerMode: true, // 突出显示“确定”按钮为红色
    }).then((willWol) => {
        if (!willWol) return; // 用户取消

        window.scrollTo({ top: 0 });
        addFlashMessage("正在唤醒全部设备，请等待结果返回...");

        fetch(`/device/wol/all?key=${KEY}`, { method: 'POST' })
            .then(response => {
                if (!response.ok) addFlashMessage("请求失败：" + response.status);
                return response.json();
            })
            .then(data => {
                if (data) {
                    addFlashMessage(data.text);
                } else {
                    addFlashMessage("全部开机出现问题，请查看日志");
                }
            })
            .catch(err => {
                addFlashMessage("请求异常：" + err.message);
            });
    });
}
// 全部关机按钮
function sendShutdownAllRequest() {
    swal({
        title: "确定要全部关机吗？",
        text: "将关闭所有设备，请确保重要任务已完成。",
        icon: "warning",
        buttons: ["取消", "确定关机"],
        dangerMode: true,
    }).then((willShutdown) => {
        if (!willShutdown) return;

        window.scrollTo({ top: 0 });
        addFlashMessage("正在关闭全部设备，请等待结果返回...");

        fetch(`/device/shutdown/all?key=${KEY}`, { method: 'POST' })
            .then(response => {
                if (!response.ok) addFlashMessage("请求失败：" + response.status);
                return response.json();
            })
            .then(data => {
                if (data) {
                    addFlashMessage(data.text);
                } else {
                    addFlashMessage("全部关机出现问题，请查看日志");
                }
            })
            .catch(err => {
                addFlashMessage("请求异常：" + err.message);
            });
    });
}

// 重启容器按钮
function sendRestartContainerRequest() {
    // 弹窗确认
    swal({
        title: "确定要重启容器吗？",
        text: "请确保容器重启策略为always或unless-stopped",
        icon: "warning",
        buttons: ["取消", "确定重启"],
        dangerMode: true,
    }).then((willShutdown) => {
        if (!willShutdown) return;

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
    });
}

document.getElementById('new_device_top_btn').addEventListener('click', sendNewDeviceRequest);
document.getElementById('wol_all_top_btn').addEventListener('click', sendWolAllRequest);
document.getElementById('shutdown_all_top_btn').addEventListener('click', sendShutdownAllRequest);
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
                card.dataset.devId = deviceId; // 标记设备ID

                // 点击跳转设备编辑页 或 批量选择
                card.addEventListener('click', (e) => {
                    // 如果在批量模式，则切换选中状态
                    if (batchMode) {
                        e.stopPropagation();
                        // 排除主程序
                        if (deviceId === 'main') {
                            swal({
                                title: '不能选择主程序',
                                text: '主程序[main]不能被选中用于批量操作。',
                                icon: 'warning',
                                button: "确认",
                            });
                            return;
                        }
                        if (selectedIds.has(deviceId)) {
                            selectedIds.delete(deviceId);
                            card.classList.remove('selected');
                        } else {
                            selectedIds.add(deviceId);
                            card.classList.add('selected');
                        }
                        
                        return;
                    }

                    // 非批量模式：打开配置页
                    window.open(`/config/${deviceId}?key=${KEY}`, '_blank');
                });

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
                    swal({
                        title: "确定要开机吗？",
                        icon: "warning",
                        buttons: ["取消", "确定开机"],
                        dangerMode: true,
                    }).then((willWol) => {
                        if (!willWol) return;
                        const id = btn.getAttribute('dev-id');
                        window.scrollTo({ top: 0 });
                        addFlashMessage("正在唤醒设备，请等待结果返回...");

                        fetch(`/wol/${id}?key=${KEY}`, { method: 'GET' })
                            .then(response => {
                                if (!response.ok) addFlashMessage("请求失败：" + response.status);
                                return response.json();
                            })
                            .then(data => {
                                if (data) {
                                    const flashText = `[${data.device_name}]${data.message_cn}`;
                                    addFlashMessage(flashText);
                                } else {
                                    addFlashMessage("唤醒设备出现问题，请查看日志");
                                }
                            })
                            .catch(err => {
                                addFlashMessage("请求异常：" + err.message);
                            });
                    });
                });
            });
            container.querySelectorAll('.power-off').forEach(btn => {
                btn.addEventListener('click', e => {
                    e.stopPropagation();
                    swal({
                        title: "确定要关机吗？",
                        icon: "warning",
                        buttons: ["取消", "确定关机"],
                        dangerMode: true,
                    }).then((willShutdown) => {
                        if (!willShutdown) return;
                        const id = btn.getAttribute('dev-id');
                        window.scrollTo({ top: 0 });
                        addFlashMessage("正在关闭设备，请等待结果返回...");
                        fetch(`/shutdown/${id}?key=${KEY}`, { method: 'GET' })
                            .then(response => {
                                if (!response.ok) addFlashMessage("请求失败：" + response.status);
                                return response.json();
                            })
                            .then(data => {
                                if (data) {
                                    const flashText = `[${data.device_name}]${data.message_cn}`;
                                    addFlashMessage(flashText);
                                } else {
                                    addFlashMessage("关闭设备出现问题，请查看日志");
                                }
                            })
                            .catch(err => {
                                addFlashMessage("请求异常：" + err.message);
                            });
                    });
                });
            });

            
        })
        .catch(err => {
            container.innerHTML = '<p>无法加载设备信息，请检查网络或刷新页面。</p>';
            console.error(err);
        });
};
// ----------------------------------------------------------------------------------------------------
// 批量模式
let batchMode = false;
const selectedIds = new Set();
const batchToggleBtn = document.getElementById('batch_operation_top_btn');
const batchBtnLine = document.getElementById('batch_btn_line');

function enterBatchMode() {
    batchMode = true;
    batchToggleBtn.textContent = '退出批量';
    batchToggleBtn.style.backgroundColor = '#ff6666';
    batchBtnLine.classList.remove('hidden');
    batchBtnLine.classList.add('visible');
    // 获取所有 .card-actions 元素
    const cardActionsElements = document.querySelectorAll('.card-actions');
    // 遍历并添加 hidden class
    cardActionsElements.forEach(el => {
        el.classList.remove('visible');
        el.classList.add('hidden');
    });
    // 进入批量模式时停止自动刷新，避免选中状态被刷新覆盖
    stopAutoRefresh();
}

function exitBatchMode() {
    batchMode = false;
    batchToggleBtn.textContent = '批量操作';
    batchToggleBtn.style.backgroundColor = '';
    batchBtnLine.classList.remove('visible');
    batchBtnLine.classList.add('hidden');
    const cardActionsElements = document.querySelectorAll('.card-actions');
    cardActionsElements.forEach(el => {
        el.classList.remove('hidden');
        el.classList.add('visible');
    });
    // 清除所有选中样式
    selectedIds.clear();
    document.querySelectorAll('.device-card.selected').forEach(el => {
        el.classList.remove('selected');
        el.style.border = '';
        el.style.background = '';
    });

    // 退出批量模式后恢复自动刷新
    startAutoRefresh();
}

function toggleBatchMode() {
    if (batchMode) exitBatchMode();
    else enterBatchMode();
}

// 绑定批量按钮切换
if (batchToggleBtn) batchToggleBtn.addEventListener('click', toggleBatchMode);

// 绑定批量操作顶部按钮事件（将选中的设备 ID 发送到后端）
function sendBatchAction(action) {
    if (selectedIds.size === 0) {
        swal({
            title: '请先选择至少一个设备',
            icon: 'warning',
            button: "确认",
        });
        return;
    }

    let actionCN = '';
    if (action === 'wol') {
        actionCN = '开机';
    } else if (action === 'shutdown') {
        actionCN = '关机';
    } else if (action === 'start') {
        actionCN = '启动服务';
    } else if (action === 'stop') {
        actionCN = '停止服务';
    } else if (action === 'restart') {
        actionCN = '重启服务';
    } else if (action === 'delete') {
        actionCN = '删除配置';
    } else {
        actionCN = '未知操作';
    }

    swal({
        title: `确定要批量${actionCN}吗？`,
        icon: "warning",
        buttons: ["取消", "确定"],
        dangerMode: true,
    }).then((willOperate) => {
        if (!willOperate) return;
        const ids = Array.from(selectedIds);
        window.scrollTo({ top: 0 });
        addFlashMessage(`正在执行批量操作：${actionCN}，设备数量：${ids.length}，请等待结果返回...`);

        fetch(`/device/batch/${action}?key=${KEY}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ device_ids: ids })
        })
            .then(response => {
                if (!response.ok) addFlashMessage('请求失败：' + response.status);
                return response.json();
            })
            .then(data => {
                if (data) {
                    addFlashMessage(data.text || JSON.stringify(data));
                    // 操作完成后刷新设备列表并退出批量模式
                    exitBatchMode();
                    fetchAllDevicesBrief();
                } else {
                    addFlashMessage('批量操作返回为空，请查看日志');
                }
            })
            .catch(err => {
                addFlashMessage('请求异常：' + err.message);
            });
    });
}
// 绑定顶部批量操作按钮
const wolBatchBtn = document.getElementById('wol_batch_top_btn');
const shutdownBatchBtn = document.getElementById('shutdown_batch_top_btn');
const startBatchBtn = document.getElementById('start_batch_top_btn');
const stopBatchBtn = document.getElementById('stop_batch_top_btn');
const restartBatchBtn = document.getElementById('restart_batch_top_btn');
const deleteBatchBtn = document.getElementById('delete_batch_top_btn');
const selectAllToggleBtn = document.getElementById('select_all_toggle_top_btn');

if (wolBatchBtn) wolBatchBtn.addEventListener('click', () => sendBatchAction('wol'));
if (shutdownBatchBtn) shutdownBatchBtn.addEventListener('click', () => sendBatchAction('shutdown'));
if (startBatchBtn) startBatchBtn.addEventListener('click', () => sendBatchAction('start'));
if (stopBatchBtn) stopBatchBtn.addEventListener('click', () => sendBatchAction('stop'));
if (restartBatchBtn) restartBatchBtn.addEventListener('click', () => sendBatchAction('restart'));
if (deleteBatchBtn) deleteBatchBtn.addEventListener('click', () => sendBatchAction('delete'));
if (selectAllToggleBtn) selectAllToggleBtn.addEventListener('click', () => {
    // 切换：如果所有可选设备都已被选中，则取消全部；否则全选（排除 main）
    const allCards = Array.from(container.querySelectorAll('.device-card'));
    const selectableIds = allCards.map(c => c.dataset.devId).filter(id => id && id !== 'main');
    const allSelected = selectableIds.every(id => selectedIds.has(id));
    if (allSelected) {
        // 取消全部
        selectableIds.forEach(id => {
            selectedIds.delete(id);
            const el = container.querySelector(`.device-card[data-dev-id="${id}"]`);
            if (el) el.classList.remove('selected');
        });
    } else {
        // 全选
        selectableIds.forEach(id => {
            selectedIds.add(id);
            const el = container.querySelector(`.device-card[data-dev-id="${id}"]`);
            if (el) el.classList.add('selected');
        });
    }

});

// 新增：自动刷新定时器 ID 与控制函数
let refreshIntervalId = null;
function startAutoRefresh() {
    if (refreshIntervalId) return;
    refreshIntervalId = setInterval(fetchAllDevicesBrief, 5000);
}
function stopAutoRefresh() {
    if (!refreshIntervalId) return;
    clearInterval(refreshIntervalId);
    refreshIntervalId = null;
}

// 页面加载调用
window.addEventListener('DOMContentLoaded', () => {
    fetchAllDevicesBrief();
    // 启动自动刷新
    startAutoRefresh();
});