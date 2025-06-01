// config.html

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
// 获取当前页面的 URL
const currentUrl = new URL(window.location.href);
// 获取 URL 中的 key 参数
const key = currentUrl.searchParams.get('key');
// 如果 key 参数存在，则修改相关跳转
if (key) {
    var form = document.getElementById('restart');
    form.action = `/restart?key=${key}`;
    document.getElementById('logs').href = `/logs?key=${key}`;
    document.getElementById('go_wol').href = `/wol?key=${key}`;
    document.getElementById('go_shutdown').href = `/shutdown?key=${key}`;
    document.getElementById('go_ping').href = `/ping?key=${key}`;
    document.getElementById('go_push').href = `/testpush?key=${key}`;
}
// 监听表单提交事件
document.getElementById('restart').addEventListener('submit', function (event) {
    event.preventDefault(); // 防止表单默认提交

    // 使用 Fetch API 发送 POST 请求（不关心响应）
    fetch(form.action, {
        method: 'POST',
    })
    // 初始化倒计时
    let countdown = 5;

    // 添加 "即将刷新" 消息
    const flashMessages = document.getElementById('flash-messages');
    const messageElement = document.createElement('ul');
    const messageItem = document.createElement('li');
    messageItem.innerHTML = `即将刷新 ${countdown}`;
    messageElement.appendChild(messageItem);
    flashMessages.appendChild(messageElement);

    // 设置定时器每秒更新一次消息
    const intervalId = setInterval(function () {
        countdown--;
        messageItem.innerHTML = `即将刷新 ${countdown}`; // 更新提示消息

        // 倒计时结束后刷新页面
        if (countdown < 1) {
            clearInterval(intervalId); // 清除定时器
            location.reload(); // 刷新页面
        }
    }, 1000); // 每隔1秒更新一次 
});

// ----------------------------------------------------------------------------------------------------
function go_func_show() {
    const items = [
        'bemfa', 'wol', 'shutdown', 'ping', 'push',
        'serverchanturbo', 'serverchan3', 'qmsg', 'wechat_webhook'
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
    const checkboxes = document.querySelectorAll('.checkbox-label:not(#bemfa_reconnect_enabled)');

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
// 获取复选框和目标内容元素
const netrpcCheckbox = document.getElementById('netrpc');
const udpCheckbox = document.getElementById('udp');
const shellCheckbox = document.getElementById('shell');
const netrpcConfig = document.getElementById('netrpcconfig');
const dl_pcshutdown = document.getElementById('dl_pcshutdown');
const shell_script = document.getElementById('shell_script');
const shutdown_delay_time = document.getElementById('shutdown_delay_time');

// 更新netrpcconfig的显示状态
function ifshow_method_shutdown() {
    function showElement(element) {
        element.classList.remove('hidden');
        element.classList.add('visible');
    }

    function hideElement(element) {
        element.classList.remove('visible');
        element.classList.add('hidden');
    }

    hideElement(netrpcConfig);
    hideElement(dl_pcshutdown);
    hideElement(shell_script);
    hideElement(shutdown_delay_time);

    if (netrpcCheckbox.checked) {
        showElement(netrpcConfig);
        showElement(shutdown_delay_time);
    } else if (udpCheckbox.checked) {
        showElement(dl_pcshutdown);
        showElement(shutdown_delay_time);
    } else if (shellCheckbox.checked) {
        showElement(shell_script);
    }
}

// 勾选一个复选框时，取消另一个复选框的勾选
function only_one_check(checkedCheckbox) {
    const checkboxes = [netrpcCheckbox, udpCheckbox, shellCheckbox];
    checkboxes.forEach(checkbox => {
        // 如果当前复选框被勾选的复选框，则勾选
        if (checkbox !== checkedCheckbox) {
            checkbox.checked = false;
        }
    });
    ifshow_method_shutdown();
}

// 监听
function handleCheckboxChange(checkbox) {
    if (checkbox.checked) {
        only_one_check(checkbox);
    } else {
        checkbox.checked = true;  // 禁止取消勾选
    }
}

document.addEventListener('DOMContentLoaded', () => {
    ifshow_method_shutdown();

    // 添加change事件监听
    netrpcCheckbox.addEventListener('change', () => handleCheckboxChange(netrpcCheckbox));
    udpCheckbox.addEventListener('change', () => handleCheckboxChange(udpCheckbox));
    shellCheckbox.addEventListener('change', () => handleCheckboxChange(shellCheckbox));
});

// ----------------------------------------------------------------------------------------------------
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
            input.style.width = `${tempSpan.offsetWidth + 10}px`;

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