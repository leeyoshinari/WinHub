function plot_chart(myChart, x, y1, y2, y3, label1, label2, label3, ylabel1, ylabel2, y2AxisIndex) {
    option = {
        grid: [{left: '5%', right: '5%', top: 50, height: 300}],
        tooltip: {trigger: 'axis', axisPointer: {type: 'cross'}},
        color: ['red'],
        legend: [{data: [label1], x: 'center', y: 25, icon: 'line'}],
        xAxis: [{gridIndex: 0, type: 'category', boundaryGap: false, data: x, axisTick: {alignWithLabel: true, interval: 'auto'}, axisLabel: {interval: 'auto', showMaxLabel: true}}],
        yAxis: [{gridIndex: 0, name: ylabel1, type: 'value'}],
        series: [{name: label1, type: 'line', xAxisIndex: 0, yAxisIndex: 0, showSymbol: false, lineStyle: {width: 1, color: 'red'}, data: y1}]
    };
    if (y2.length > 1) {
        option.color.push('blue');
        option.legend[0].data.push(label2);
        option.series.push({name: label2, type: 'line', xAxisIndex: 0, yAxisIndex: y2AxisIndex, showSymbol: false, lineStyle: {width: 1, color: 'blue'}, data: y2});
    }
    if (y3.length > 1) {
        option.color.push('orange');
        option.legend[0].data.push(label3);
        option.series.push({name: label3, type: 'line', xAxisIndex: 0, yAxisIndex: 1, showSymbol: false, lineStyle: {width: 1, color: 'orange'}, data: y3});
    }
    if (ylabel2 !== "") {
        option.yAxis.push({gridIndex: 0, name: ylabel2, type: 'value'});
    }
    myChart.clear();
    myChart.setOption(option);
}
