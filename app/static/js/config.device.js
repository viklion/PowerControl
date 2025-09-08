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
    const timestamp = now.toISOString().slice(0, 19).replace("T", " "); // 格式: YYYY-MM-DD HH:MM:SS
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
    fetch(`/device/restart/${DEVICE_ID}?key=${KEY}`, {method: 'POST'})
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
    if (!confirm("确定要删除该设备服务吗？")) {
        return; // 用户取消，直接返回
    }
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
    const checkboxes = document.querySelectorAll('.checkbox-label:not(#main_enabled):not(#push_enabled)');

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
});

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
const dl_pcshutdown = document.getElementById('dl_pcshutdown');
const shutdown_shell_script = document.getElementById('shutdown_shell_script');
const shutdown_delay_time = document.getElementById('shutdown_delay_time');

// 更新显示状态
function ifshow_method_shutdown() {
    hideElement(netrpcConfig);
    hideElement(dl_pcshutdown);
    hideElement(shutdown_shell_script);
    hideElement(shutdown_delay_time);

    if (shutdownMethodSelect.value === 'netrpc') {
        showElement(netrpcConfig);
        showElement(shutdown_delay_time);
    } else if (shutdownMethodSelect.value === 'udp') {
        showElement(dl_pcshutdown);
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