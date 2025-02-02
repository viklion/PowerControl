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
// 跳转按钮
document.addEventListener("DOMContentLoaded", function () {
    let input = document.getElementById("webkey");
    let button = document.getElementById("keybtn");
    let message = document.getElementById("message");

    function sendKey() {
        let key = input.value
        fetch("/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ key: key })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = `/config?key=${key}`;
                } else {
                    message.textContent = data.message; // 显示错误信息
                    message.classList.remove("hidden");
                    message.classList.add("visible");
                    setTimeout(() => {
                        message.classList.remove("visible");
                        message.classList.add("hidden");
                    }, 3000); // 3 秒后清空
                }
            })
            .catch(error => console.error("Error:", error));
    }

    // 监听按钮点击
    button.addEventListener("click", sendKey);

    // 监听输入框按键
    input.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault(); // 防止刷新页面
            sendKey();
        }
    });
});
// ----------------------------------------------------------------------------------------------------