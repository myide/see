<template>
    <div style="width:100%;height:100%;" id="data_source_con"></div>
</template>

<script>
import echarts from 'echarts';

export default {
    name: 'dataSourcePie',
    data () {
        return {
            chart:{}
        };
    },
    props: ['sqlStatusChart'],
    created() {
        const sqlStatusChart = this.sqlStatusChart
        for (let i in sqlStatusChart) {
            const item = sqlStatusChart[i]
            this.chart[item.status.toString()] = item.num
        }
    },
    mounted () {
        this.$nextTick(() => {
            var dataSourcePie = echarts.init(document.getElementById('data_source_con'));

            window.addEventListener('resize', function () {
                dataSourcePie.resize();
            }); 

            dataSourcePie.setOption( 
                {
                    tooltip: {
                        trigger: 'item',
                        formatter: '{a} <br/>{b} : {c} ({d}%)'
                    },
                    legend: {
                        orient: 'vertical',
                        left: 'right',
                        data: ['已回滚', '已暂停', '待执行', '已执行', '已放弃', '执行失败']
                    },
                    series: [
                        {
                            name: 'SQL工单状态',
                            type: 'pie',
                            radius: '66%',
                            center: ['50%', '60%'],
                            data: [
                                {value: this.chart['-3'], name: '已回滚', itemStyle: {normal: {color: '#9bd598'}}},
                                {value: this.chart['-2'], name: '已暂停', itemStyle: {normal: {color: '#ffd58f'}}},
                                {value: this.chart['-1'], name: '待执行', itemStyle: {normal: {color: '#abd5f2'}}},
                                {value: this.chart['0'], name: '已执行', itemStyle: {normal: {color: '#ab8df2'}}},
                                {value: this.chart['1'], name: '已放弃', itemStyle: {normal: {color: '#e14f60'}}},
                                {value: this.chart['2'], name: '执行失败', itemStyle: {normal: {color: '#0066FF'}}},
                            ],
                            itemStyle: {
                                emphasis: {
                                    shadowBlur: 10,
                                    shadowOffsetX: 0,
                                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                                }
                            }
                        }
                    ]
                } 

        )

        });
    }
};
</script>
