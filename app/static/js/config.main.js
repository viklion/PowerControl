// config-main.html
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
document.getElementById('go_push').href = `/message/test?key=${KEY}`;

// ----------------------------------------------------------------------------------------------------
// 根据复选框状态更新跳转链接的显示或隐藏
function go_func_show() {
    const items = [
        'push', 'serverchanturbo', 'serverchan3', 'qmsg', 'gotify',
        'pushplus', 'bark', 'wechat_webhook', 'wechat_app'
        
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