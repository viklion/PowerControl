// logs.html

// 加载文件内容
function loadFileContent(filename, listItem) {
    // 取消其他文件的选中状态
    const allItems = document.querySelectorAll('.file-list li');
    allItems.forEach(item => item.classList.remove('selected'));

    // 高亮当前选择的文件
    listItem.classList.add('selected');

    // 更新文件名
    document.getElementById('fileName').textContent = filename;

    // 获取当前页面的 URL
    const currentUrl = new URL(window.location.href);
    // 获取 URL 中的 key 参数
    const key = currentUrl.searchParams.get('key');
    // 构造 fetch 请求的 URL，带上 key 参数
    const fetchUrl = `/logs/${filename}?key=${key}`;

    // 请求文件内容
    fetch(fetchUrl)
        .then(response => response.json())
        .then(data => {
            // 获取日志内容
            let logContent = data.log_content;

            // 将日志内容按行分割
            const lines = logContent.split('\n');

            // 遍历每一行，检查是否包含 '[Error]'，如果是，则添加红色样式
            const formattedLines = lines.map(line => {
                if (line.includes('[Error]')) {
                    return `<span class="error-line">${line}</span>`;
                }
                return line;
            });

            // 将处理后的日志内容插入到页面
            document.getElementById('fileContent').innerHTML = formattedLines.join('<br>');

            // 显示删除按钮并绑定当前文件名
            const deleteButton = document.getElementById('deleteButton');
            deleteButton.style.display = 'block'; // 显示删除按钮
            deleteButton.onclick = function () {
                deleteFile(filename); // 将当前文件名传给删除函数
            };

            // 使用 DOM 的 scrollTop 属性将内容区域滚动到顶部
            const contentArea = document.getElementById('contentArea');
            contentArea.scrollTop = 0;  // 直接将 scrollTop 设置为 0
        })
        .catch(error => alert('无法加载文件内容: ' + error));

    // 点击文件后自动隐藏文件列表（仅移动端）
    if (window.innerWidth <= 768) {
        toggleSidebar();
    }
}

// 删除日志文件
function deleteFile(filename) {
    if (confirm('确定要删除该日志文件吗?')) {
        // 获取当前页面的 URL
        const currentUrl = new URL(window.location.href);
        // 获取 URL 中的 key 参数
        const key = currentUrl.searchParams.get('key');
        const deleteUrl = `/logs/delete/${filename}?key=${key}`;

        // 发送删除请求
        fetch(deleteUrl, {
            method: 'DELETE',
        })
            .then(response => {
                if (response.ok) {
                    console.log(`已手动删除日志：${filename}`);
                    // 删除文件后刷新页面
                    window.location.reload();
                } else {
                    alert('删除失败，请稍后重试');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('删除过程中发生错误');
            });
    }
}

// 切换文件列表的显示与隐藏
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const button = document.getElementById('toggleButton');

    // 判断文件列表是否显示
    if (sidebar.classList.contains('open')) {
        sidebar.classList.remove('open');
        button.textContent = '>'; // 显示右箭头
    } else {
        sidebar.classList.add('open');
        button.textContent = '<'; // 显示左箭头
    }
}

// 页面加载时显示切换按钮（移动端）
window.addEventListener('resize', function () {
    const button = document.getElementById('toggleButton');
    const sidebar = document.getElementById('sidebar');
    if (window.innerWidth > 768) {
        button.style.display = 'none'; // 隐藏切换按钮
        sidebar.classList.add('open'); // 始终显示文件列表
    } else {
        button.style.display = 'block'; // 显示切换按钮
        sidebar.classList.remove('open'); // 隐藏文件列表
    }
});

// 初始加载时处理屏幕尺寸并确保文件列表弹出（手机端）
window.addEventListener('load', function () {
    if (window.innerWidth <= 768) {
        const sidebar = document.getElementById('sidebar');
        sidebar.classList.add('open'); // 移动端首次加载时自动显示文件列表
        document.getElementById('toggleButton').textContent = '<'; // 设置按钮为左箭头
    }
});

// 点击非列表区域时收起文件列表
document.addEventListener('click', function (event) {
    const sidebar = document.getElementById('sidebar');
    const button = document.getElementById('toggleButton');
    const sidebarArea = sidebar.contains(event.target);
    const buttonArea = button.contains(event.target);

    if (!sidebarArea && !buttonArea && window.innerWidth <= 768) {
        sidebar.classList.remove('open');
        button.textContent = '>'; // 恢复右箭头
    }
});

// 初始加载时处理屏幕尺寸
window.dispatchEvent(new Event('resize'));

// 滚动到页面顶部
function scrollToTop() {
    const contentArea = document.getElementById('contentArea');
    contentArea.scrollTo({ top: 0, behavior: 'smooth' });
}

// 滚动到页面底部
function scrollToBottom() {
    const contentArea = document.getElementById('contentArea');
    contentArea.scrollTo({ top: contentArea.scrollHeight, behavior: 'smooth' });
}