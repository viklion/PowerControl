// index.html
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
// 如果 key 参数存在，则修改表单的 action 属性
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
    let countdown = 3;

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
    //将所有相关项的名称放在一个数组 items 中
    const items = [
        'bemfa', 'wol', 'shutdown', 'ping', 'push',
        'serverchanturbo', 'serverchan3', 'qmsg'
    ];
    //使用 forEach 方法遍历数组，对每个项进行操作
    items.forEach(item => {
        //通过模板字符串拼接出对应的 enabled 元素和 go 元素的 id
        const enabled_id = `${item}_enabled`;
        const go_id = `go_${item}`;
        //根据 enabled 元素的 checked 属性值，设置 go 元素的 display 样式
        document.getElementById(go_id).style.display =
            document.getElementById(enabled_id).checked ? '' : 'none';
    });
}

// 根据复选框状态更新对应内容的显示或隐藏
function ifshow(event) {
    const checkbox = event.target; // 当前触发事件的复选框
    const targetId = checkbox.dataset.target; // 获取对应的内容 ID
    const targetElement = document.getElementById(targetId); // 获取目标内容元素

    if (checkbox.checked) {
        targetElement.classList.remove('hidden');
    } else {
        targetElement.classList.add('hidden');
    }
    go_func_show()
}
// 页面加载完成后为所有复选框添加事件监听
document.addEventListener('DOMContentLoaded', () => {
    const checkboxes = document.querySelectorAll('.checkbox-label');

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
const dl_shell_script = document.getElementById('dl_shell_script');

// 更新netrpcconfig的显示状态
function ifshow_method_shutdown() {
    if (netrpcCheckbox.checked) {
        netrpcConfig.classList.remove('hidden');
        dl_pcshutdown.classList.add('hidden');
        dl_shell_script.classList.add('hidden');
    } else if (udpCheckbox.checked) {
        dl_pcshutdown.classList.remove('hidden');
        netrpcConfig.classList.add('hidden');
        dl_shell_script.classList.add('hidden');
    }else if (shellCheckbox.checked) {
        dl_shell_script.classList.remove('hidden');
        netrpcConfig.classList.add('hidden');
        dl_pcshutdown.classList.add('hidden');
    }
}

// 勾选一个复选框时，取消另一个复选框的勾选
function only_one_check_netrpc() {
    if (netrpcCheckbox.checked) {
        udpCheckbox.checked = false;
        shellCheckbox.checked = false;
    }
    ifshow_method_shutdown();
}
function only_one_check_udp() {
    if (udpCheckbox.checked) {
        netrpcCheckbox.checked = false;
        shellCheckbox.checked = false;
    }
    ifshow_method_shutdown();
}
function only_one_check_shell() {
    if (shellCheckbox.checked) {
        netrpcCheckbox.checked = false;
        udpCheckbox.checked = false;
    }
    ifshow_method_shutdown();
}

// 初始化状态
document.addEventListener('DOMContentLoaded', () => {
    ifshow_method_shutdown();

    // 添加change事件监听
    netrpcCheckbox.addEventListener('change', only_one_check_netrpc);
    udpCheckbox.addEventListener('change', only_one_check_udp);
    shellCheckbox.addEventListener('change', only_one_check_shell);
});
// ----------------------------------------------------------------------------------------------------
function submit_pcconfig() {
    document.getElementById("pcconfig").submit();
}

// ----------------------------------------------------------------------------------------------------

