let i18nList = document.getElementsByClassName('i18n');
for (let i=0; i<i18nList.length; i++) {i18nList[i].innerText = window.parent.i18next.t(i18nList[i].getAttribute('key'));}
let apps = {
    taskmgr: {
        cpu: 0,
        cpuChart: null,
        cpuBg: null,
        memory: 0,
        memoryInfo: {total: 0, free: 0, used: 0, available: 0},
        memoryChart: null,
        memoryBg: null,
        disk: 0,
        disk2Chart: null,
        disk2Bg: null,
        diskSpeed: {read: 0, write: 0},
        wifi: {receive: 0, send: 0},
        wifiChart: null,
        wifiBg: null,
        handle: 0,
        load: (init_all = true) => {
            if (init_all === true) {
                apps.taskmgr.cpuChart = $('.performance-graph>.graph-cpu>.graph>.chart')[0];
                apps.taskmgr.cpuBg = $('.performance-graph>.graph-cpu>.graph>.bg')[0];
                apps.taskmgr.cpuBg.innerHTML = '<g class="col"></g><g class="row"></g>';
                apps.taskmgr.cpuChart.innerHTML = '<path d="M 6000 1000" stroke="#2983cc" stroke-width="3px" fill="#2983cc22" />';

                apps.taskmgr.memoryChart = $('.performance-graph>.graph-memory>.graph>.chart')[0];
                apps.taskmgr.memoryBg = $('.performance-graph>.graph-memory>.graph>.bg')[0];
                apps.taskmgr.memoryBg.innerHTML = '<g class="col"></g><g class="row"></g>';
                apps.taskmgr.memoryChart.innerHTML = '<path d="M 6000 1000" stroke="#660099" stroke-width="3px" fill="#66009922" />';
                apps.taskmgr.disk2Chart = $('.performance-graph>.graph-disk>.graph>.chart')[0];
                apps.taskmgr.disk2Bg = $('.performance-graph>.graph-disk>.graph>.bg')[0];
                apps.taskmgr.disk2Bg.innerHTML = '<g class="col"></g><g class="row"></g>';
                apps.taskmgr.disk2Chart.innerHTML = '<path d="M 6000 1000" stroke="#008000" stroke-width="3px" fill="#00800022" /><path d="M 6000 1000" stroke="#008000" stroke-width="3px" fill="none" stroke-dasharray="15, 15" />';
                apps.taskmgr.wifiChart = $('.graph-wifi>.graph>.chart')[0];
                apps.taskmgr.wifiBg = $('.graph-wifi>.graph>.bg')[0];
                apps.taskmgr.wifiChart.innerHTML = '<path d="M 6000 1000" stroke="#8e5829" stroke-width="3px" fill="#8e582922" /><path d="M 6000 1000" stroke="#8e5829" stroke-width="3px" fill="none" stroke-dasharray="10, 10" />';
                apps.taskmgr.wifiBg.innerHTML = '<g class="col"></g><g class="row"></g>';
            }
            if (init_all === true) {
                apps.taskmgr.generateProcesses();
                apps.taskmgr.performanceLoad();
                apps.taskmgr.drawGrids();
                apps.taskmgr.handle = window.setInterval(() => {
                    apps.taskmgr.generateProcesses();
                    apps.taskmgr.performanceLoad();
                    apps.taskmgr.loadGraph();
                    apps.taskmgr.gridLine();
                }, 2000);
            }
        },
        graph: (name) => {
            $('.main>.cnt.performance>.content>.performance-graph>.show').removeClass('show');
            $('.main>.cnt.performance>.content>.performance-graph>.' + name).addClass('show');
            $('.main>.cnt.performance>.content>.select-menu>.check').removeClass('check');
            $('.main>.cnt.performance>.content>.select-menu>.' + name).addClass('check');
            apps.taskmgr.getSystemInfo(name);
        },
        generateProcesses: () => {
            window.parent.$.ajax({
                type: 'GET',
                url: localStorage.getItem('server') + '/system/resource',
                success: function (data) {
                    if (data.code === 0) {
                        apps.taskmgr.cpu = data.data.cpu;
                        apps.taskmgr.memory = data.data.memory_percent;
                        apps.taskmgr.memoryInfo.total = data.data.total_memory;
                        apps.taskmgr.memoryInfo.used = data.data.used_memory;
                        apps.taskmgr.memoryInfo.free = data.data.free_memory;
                        apps.taskmgr.memoryInfo.available = data.data.available_memory;
                        apps.taskmgr.diskSpeed.read = data.data.io_read;
                        apps.taskmgr.diskSpeed.write = data.data.io_write;
                        apps.taskmgr.wifi.receive = data.data.net_recv;
                        apps.taskmgr.wifi.send = data.data.net_sent;
                    } else {
                        window.parent.$.Toast(data['msg'], 'error');
                    }
                }
            })
        },
        performanceLoad: () => {
            $('.main>.cnt.performance>.content>.select-menu>.graph-cpu>.right>.data>.value1')[0].innerText = `${apps.taskmgr.cpu}%`;
            $('.main>.cnt.performance>.content>.performance-graph>.graph-memory>.information>.left>div:nth-child(1)>.value')[0].innerText = `${apps.taskmgr.memoryInfo.total} GB`;
            $('.main>.cnt.performance>.content>.performance-graph>.graph-memory>.information>.left>div:nth-child(2)>.value')[0].innerText = `${apps.taskmgr.memoryInfo.used} GB`;
            $('.main>.cnt.performance>.content>.performance-graph>.graph-memory>.information>.left>div:nth-child(3)>.value')[0].innerText = `${apps.taskmgr.memoryInfo.available} GB`;
            $('.main>.cnt.performance>.content>.performance-graph>.graph-memory>.information>.left>div:nth-child(4)>.value')[0].innerText = `${apps.taskmgr.memoryInfo.free} GB`;
            $('.main>.cnt.performance>.content>.select-menu>.graph-memory>.right>.data>.value1')[0].innerText = `${apps.taskmgr.memory}%`;

            $('.main>.cnt.performance>.content>.performance-graph>.graph-disk>.information>.left>div:nth-child(3)>.value')[0].innerText = `${apps.taskmgr.diskSpeed.read} MB/s`;
            $('.main>.cnt.performance>.content>.performance-graph>.graph-disk>.information>.left>div:nth-child(4)>.value')[0].innerText = `${apps.taskmgr.diskSpeed.write} MB/s`;

            $('.main>.cnt.performance>.content>.performance-graph>.graph-wifi>.information>.left>div:nth-child(1)>.value')[0].innerText = `${apps.taskmgr.wifi.send} Mbps`;
            $('.main>.cnt.performance>.content>.performance-graph>.graph-wifi>.information>.left>div:nth-child(2)>.value')[0].innerText = `${apps.taskmgr.wifi.receive} Mbps`;
        },
        drawGraph: (chart, data, nth = 0) => {
            let path = $(chart.querySelectorAll('path')[nth]).attr('d');
            path = path.replace(/ L 6000 1000$/, '');
            let pathl = path.split(' ');
            let newPath = '';
            let sum = 0, head = 0;
            for (let i = 0; i < pathl.length; i += 3) {
                const arg = pathl[i];
                if (arg === 'M' && Number(pathl[i + 1]) > 0) {
                    pathl[i + 1] = Number(pathl[i + 1]) - 100;
                    pathl[i + 2] = pathl[i + 2];
                }
                else if (arg === 'M' && Number(pathl[i + 1]) <= 0) {
                    pathl[i + 1] = 0;
                    pathl[i + 2] = 1000;
                }
                else if (arg === 'L') {
                    if (sum === 0) {
                        head = i;
                    }
                    else if (sum >= 60) {
                        pathl.splice(head, 3);
                        sum--;
                        i -= 3;
                    }
                    pathl[i + 1] = Number(pathl[i + 1]) - 100;
                    sum++;
                }
            }
            pathl.push('L', '6000', 1000 - data, 'L', '6000', '1000');
            window.setTimeout(() => {
                $(chart.querySelectorAll('path')[nth]).attr('d', '');
                for (const arg of pathl) {
                    if (!(arg === '')) {
                        newPath += arg + ' ';
                    }
                }
                newPath = newPath.substring(0, newPath.length - 1);
                $(chart.querySelectorAll('path')[nth]).attr('d', newPath);
            }, 0);
        },
        loadGraph: () => {
            apps.taskmgr.drawGraph(apps.taskmgr.cpuChart, apps.taskmgr.cpu * 10);
            apps.taskmgr.drawGraph(apps.taskmgr.memoryChart, apps.taskmgr.memory * 10);
            apps.taskmgr.drawGraph(apps.taskmgr.disk2Chart, apps.taskmgr.diskSpeed.read * 20, 0);
            apps.taskmgr.drawGraph(apps.taskmgr.disk2Chart, apps.taskmgr.diskSpeed.write * 20, 1);
            apps.taskmgr.drawGraph(apps.taskmgr.wifiChart, apps.taskmgr.wifi.receive * 20, 0);
            apps.taskmgr.drawGraph(apps.taskmgr.wifiChart, apps.taskmgr.wifi.send * 20, 1);
            $('.cnt.performance>.content>.select-menu>.graph-cpu svg')[0].innerHTML = apps.taskmgr.cpuChart.innerHTML;
            $('.cnt.performance>.content>.select-menu>.graph-memory svg')[0].innerHTML = apps.taskmgr.memoryChart.innerHTML;
            $('.cnt.performance>.content>.select-menu>.graph-disk svg')[0].innerHTML = apps.taskmgr.disk2Chart.innerHTML;
            $('.cnt.performance>.content>.select-menu>.graph-wifi svg')[0].innerHTML = apps.taskmgr.wifiChart.innerHTML;
        },
        gridLine: () => {
            apps.taskmgr.changeGrids(apps.taskmgr.memoryBg);
            apps.taskmgr.changeGrids(apps.taskmgr.cpuBg);
            apps.taskmgr.changeGrids(apps.taskmgr.disk2Bg);
            apps.taskmgr.changeGrids(apps.taskmgr.wifiBg);
        },
        initgrids: (chart) => {
            const column = chart.querySelector('g.col'), row = chart.querySelector('g.row');
            for (let i = 0; i <= 20; i++) {
                column.innerHTML += `<path d="M ${i * 300} 0 L ${i * 300} 1000 Z" stroke="#aeaeae" fill="none" />`;
            }
            for (let i = 0; i <= 10; i++) {
                row.innerHTML += `<path d="M 0 ${i * 100} L 6000 ${i * 100} Z" stroke="#aeaeae" fill="none" />`;
            }
        },
        drawGrids: () => {
            apps.taskmgr.initgrids(apps.taskmgr.cpuBg);
            apps.taskmgr.initgrids(apps.taskmgr.memoryBg);
            apps.taskmgr.initgrids(apps.taskmgr.disk2Bg);
            apps.taskmgr.initgrids(apps.taskmgr.wifiBg);
        },
        changeGrids: (chart) => {
            const grid = chart.querySelectorAll('g.col>path');
            for (const elt of grid) {
                let path = $(elt).attr('d').split(' ');
                for (var i = 0; i < path.length; i++) {
                    if (path[i] === 'M' || path[i] === 'L') {
                        var cur = Number(path[i+1]);
                        cur -= 100;
                        if (cur < 0) {
                            cur = (300 - (-cur)) + 6000;
                        }
                        path[i+1] = String(cur);
                    }
                }
                $(elt).attr('d', '');
                let tmp = '';
                for (const comp of path) {
                    tmp += comp + ' ';
                }
                $(elt).attr('d', tmp);
            }
        },
        getSystemInfo: (name) => {
            if (name === 'graph-cpu') {apps.taskmgr.getCpuInfo();}
            if (name === 'graph-disk') {apps.taskmgr.getDiskInfo();}
            if (name === 'graph-wifi') {apps.taskmgr.getNetworkInfo();}
        },
        getCpuInfo: () => {
            window.parent.$.ajax({
                type: 'GET',
                url: localStorage.getItem('server') + '/system/cpu',
                success: function (data) {
                    if (data.code === 0) {
                        $('.main>.cnt.performance>.content>.performance-graph>.graph-cpu>.tit>.right-message')[0].innerText = `${data.data.model} (${data.data.core} ${window.parent.i18next.t('setting.window.system.resource.cpu.core')})`;
                    } else {
                        window.parent.$.Toast(data['msg'], 'error');
                    }
                }
            })
        },
        getDiskInfo: () => {
            window.parent.$.ajax({
                type: 'GET',
                url: localStorage.getItem('server') + '/system/disk',
                success: function (data) {
                    if (data.code === 0) {
                        $('.main>.cnt.performance>.content>.performance-graph>.graph-disk>.information>.left>div:nth-child(1)>.value')[0].innerText = `${data.data.total}`;
                        $('.main>.cnt.performance>.content>.performance-graph>.graph-disk>.information>.left>div:nth-child(2)>.value')[0].innerText = `${data.data.used}`;
                        $('.main>.cnt.performance>.content>.select-menu>.graph-disk>.right>.data>.value1')[0].innerText = `${data.data.usage}%`;
                    } else {
                        window.parent.$.Toast(data['msg'], 'error');
                    }
                }
            })
        },
        getNetworkInfo: () => {
            window.parent.$.ajax({
                type: 'GET',
                url: localStorage.getItem('server') + '/system/network',
                success: function (data) {
                    if (data.code === 0) {
                        $('.main>.cnt.performance>.content>.performance-graph>.graph-wifi>.information>.right>table>tbody>tr:nth-child(1)>td')[1].innerText = `${data.data.name}`;
                        $('.main>.cnt.performance>.content>.performance-graph>.graph-wifi>.information>.right>table>tbody>tr:nth-child(2)>td')[1].innerText = `${data.data.speed}`;
                        $('.main>.cnt.performance>.content>.performance-graph>.graph-wifi>.information>.right>table>tbody>tr:nth-child(3)>td')[1].innerText = `${data.data.mac}`;
                        $('.main>.cnt.performance>.content>.performance-graph>.graph-wifi>.information>.right>table>tbody>tr:nth-child(4)>td')[1].innerText = `${data.data.ipv4}`;
                        $('.main>.cnt.performance>.content>.performance-graph>.graph-wifi>.information>.right>table>tbody>tr:nth-child(5)>td')[1].innerText = `${data.data.ipv6}`;
                        $('.main>.cnt.performance>.content>.select-menu>.graph-wifi>.right>.data>.value1')[0].innerText = `${data.data.name}`;
                    } else {
                        window.parent.$.Toast(data['msg'], 'error');
                    }
                }
            })
        }
    }
}

setTimeout(() => {
    apps.taskmgr.load();
    apps.taskmgr.getCpuInfo();
    apps.taskmgr.getDiskInfo();
    apps.taskmgr.getNetworkInfo();
    }, 500)
