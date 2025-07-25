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
document.getElementById('givemecommand').addEventListener('click', function () {
    // 获取表单数据
    let formData = new FormData(document.getElementById('getcommand'));

    // 发送 AJAX 请求到后端
    fetch('/getcommand', {
        method: 'POST',
        body: formData
    })
        .then(response => response.text())  // 处理返回的数据
        .then(data => {
            // 生成 HTML 结构
            let outputHTML = `
                <pre>
                    <button class="copy-btn" data-clipboard-target="#code-command">复制代码</button>
                    <code id="code-command">
${data}
                    </code>
                </pre>
            `;

            // 插入到 commandOutput 中
            document.getElementById('commandOutput').innerHTML = outputHTML;

            // 语法高亮
            hljs.highlightAll();
        })
        .catch(error => {
            console.error('Error:', error);
        });
});

// ----------------------------------------------------------------------------------------------------
var clipboard = new ClipboardJS('.copy-btn', {
    text: function (trigger) {
        // 获取按钮对应的代码块
        var codeBlock = document.querySelector(trigger.getAttribute('data-clipboard-target'));
        // 获取代码块内容，并去掉首尾空白字符
        return codeBlock.textContent.trim();
    }
});

// 成功复制后的提示
clipboard.on('success', function (e) {
    alert('代码已复制到剪贴板!');
    e.clearSelection();
});

// 复制失败后的提示
clipboard.on('error', function (e) {
    alert('复制失败，请手动复制!');
});