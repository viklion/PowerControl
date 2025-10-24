// logs.html
document.addEventListener("touchstart", function () { }, true);

// 全局保存日志内容
let currentFilename = null;
let currentListItem = null;
let allLines = [];

// 加载日志文件
function loadFileContent(filename, listItem) {
    currentFilename = filename;
    currentListItem = listItem;
    // 取消其他文件选中状态
    document.querySelectorAll('.file-list li').forEach(item => item.classList.remove('selected'));
    listItem.classList.add('selected');
    document.getElementById('fileName').textContent = filename;

    const currentUrl = new URL(window.location.href);
    const key = currentUrl.searchParams.get('key');
    const fetchUrl = `/logs/get/${filename}?key=${key}`;

    fetch(fetchUrl)
        .then(response => response.json())
        .then(data => {
            allLines = data.log_content.split('\n');
            renderLogs(allLines);

            // 提取设备名（排除重复主程序）
            const devices = [...new Set(allLines
                .map(line => {
                    const match = line.match(/\[(.*?)\]/);
                    return match ? match[1] : null;
                })
                .filter(name => name)
            )];

            // 渲染复选框、日志行
            renderDeviceCheckboxes(devices);
            // 全选 / 全不选按钮设置可见
            document.getElementById('selectAllBtn').style.display = 'block';
            document.getElementById('deselectAllBtn').style.display = 'block';

            // 删除按钮
            const deleteButton = document.getElementById('deleteButton');
            deleteButton.style.display = 'block';
            deleteButton.onclick = () => deleteFile(filename);

            // document.getElementById('contentArea').scrollTop = 0;
        })
        .catch(error => alert('无法加载文件内容: ' + error));

    if (window.innerWidth <= 768) toggleSidebar();
}

// 渲染复选框
function renderDeviceCheckboxes(devices) {
    const container = document.getElementById('deviceCheckboxes');
    container.innerHTML = '';

    // 创建复选框
    devices.forEach(device => {
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = device;
        checkbox.id = `filter_${device}`;
        checkbox.className = 'checkbox-label';
        checkbox.checked = true; // 默认选中
        checkbox.addEventListener('change', applyFilter);

        const label = document.createElement('label');
        label.setAttribute('for', `filter_${device}`);
        label.textContent = device;

        container.appendChild(checkbox);
        container.appendChild(label);
    });

    // 全选 / 全不选按钮
    document.getElementById('selectAllBtn').onclick = () => {
        container.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = true);
        applyFilter();
    };
    document.getElementById('deselectAllBtn').onclick = () => {
        container.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
        applyFilter();
    };
}

// 根据勾选过滤日志
function applyFilter() {
    const checkedDevices = Array.from(document.querySelectorAll('#deviceCheckboxes input[type="checkbox"]:checked'))
        .map(cb => cb.value);

    const filtered = allLines.filter(line => {
        const match = line.match(/\[(.*?)\]/); // 只取第一个方括号
        if (!match) return false;
        const source = match[1]; // 日志来源
        return checkedDevices.includes(source);
    });

    renderLogs(filtered);
}

// 渲染日志内容
function renderLogs(lines) {
    const formattedLines = lines.map(line => {
        if (line.includes('[DEBUG]')) return `<span class="debug-line">${line}</span>`;
        if (line.includes('[INFO]')) return `<span class="info-line">${line}</span>`;
        if (line.includes('[WARNING]')) return `<span class="warning-line">${line}</span>`;
        if (line.includes('[ERROR]')) return `<span class="error-line">${line}</span>`;
        return line;
    });

    document.getElementById('fileContent').innerHTML = formattedLines.join('<br>');
}

// 删除日志文件
function deleteFile(filename) {
    swal({
        title: "确定要删除该日志文件吗?",
        buttons: ["取消", "确定删除"],
        dangerMode: true,
    }).then((willDelete) => {
        if (!willDelete) return;

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
    });
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
    const contentArea = document.getElementById('logArea');
    contentArea.scrollTo({ top: 0, behavior: 'smooth' });
}

// 滚动到页面底部
function scrollToBottom() {
    const contentArea = document.getElementById('logArea');
    contentArea.scrollTo({ top: contentArea.scrollHeight, behavior: 'smooth' });
}

// 刷新当前日志
function refreshLog() {
    if (currentFilename) {
        loadFileContent(currentFilename, currentListItem);
    }
}