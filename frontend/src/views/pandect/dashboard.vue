<style lang="less">
    @import "./home.less";
    @import "../../styles/common.less";
</style>
<template>
    <div class="home-main">
        <Row :gutter="10">
            <Col :md="24" :lg="8">
                <Row class-name="home-page-row1" :gutter="10">
                    <Col :md="12" :lg="24" :style="{marginBottom: '10px'}">
                        <Card>
                            <Row type="flex" class="user-infor">
                                <Col span="24" style="padding-left:6px;">
                                    <Row class-name="made-child-con-middle" type="flex" align="middle">
                                        <div>
                                            <b class="card-user-infor-name" style="margin-left:50%">{{userInfo.username}}</b>
                                            <p><span style="margin-right:20px">身份：{{identity}} </span> <span>属组：{{userInfo.group}} </span></p>
                                        </div>
                                    </Row>
                                </Col>
                            </Row>
                            <div class="line-gray"></div>
                            <Row class="margin-top-8">
                                <Col span="8"><p class="notwrap">加入时间:</p></Col>
                                <Col span="16" class="padding-left-8">{{getDateJoined}}</Col>
                            </Row>
                        </Card>
                    </Col>
                    <Col :md="12" :lg="24" :style="{marginBottom: '10px'}">
                        <Card>
                            <p slot="title" class="card-title">
                                <Icon type="android-checkbox-outline"></Icon>
                                今日SQL工单
                            </p>
                            <div>
                                <Table :columns="columnsSqlToday" :data="sqlList" height="220"></Table>
                            </div>
                        </Card>
                    </Col>
                </Row>
            </Col>
            <Col :md="24" :lg="16">
                <Row :gutter="5" v-if="flag">
                    <Col :xs="24" :sm="12" :md="6" :style="{marginBottom: '10px'}">
                        <infor-card
                            id-name="user_created_count"
                            :end-val="count.sql_total"
                            iconType="upload"
                            color="#2d8cf0"
                            intro-text="SQL工单总数"
                        ></infor-card>
                    </Col>
                    <Col :xs="24" :sm="12" :md="6" :style="{marginBottom: '10px'}">
                        <infor-card
                            id-name="visit_count"
                            :end-val="count.sql_handled"
                            iconType="ios-eye"
                            color="#64d572"
                            :iconSize="50"
                            intro-text="已处理SQL工单总数"
                        ></infor-card>
                    </Col>
                    <Col :xs="24" :sm="12" :md="6" :style="{marginBottom: '10px'}">
                        <infor-card
                            id-name="collection_count"
                            :end-val="count.user_total"
                            iconType="android-person-add"
                            color="#ffd572"
                            intro-text="平台用户数"
                        ></infor-card>
                    </Col>
                    <Col :xs="24" :sm="12" :md="6" :style="{marginBottom: '10px'}">
                        <infor-card
                            id-name="transfer_count"
                            :end-val="count.group_total"
                            iconType="shuffle"
                            color="#f25e43"
                            intro-text="平台组数"
                        ></infor-card>
                    </Col>
                </Row>

                <Row>
                    <Col :md="24" :lg="12" :style="{marginBottom: '10px'}">
                        <Card>
                            <p slot="title" class="card-title">
                                <Icon type="ios-pulse-strong"></Icon>
                                SQL工单状态统计
                            </p>
                            <div class="data-source-row" style="height:250px">
                                <data-source-pie v-if="flag" :sqlStatusChart="sqlStatusChart"></data-source-pie>
                            </div>
                        </Card>
                    </Col>

                    <Col :md="24" :lg="12" :style="{marginBottom: '10px'}">
                        <Card>
                            <p slot="title" class="card-title">
                                <Icon type="android-map"></Icon>
                                SQL语句类型统计
                            </p>
                            <div class="data-source-row" style="height:250px">
                                <visite-volume v-if="flag" :sqlTypeChart="sqlTypeChart"></visite-volume>
                            </div>
                        </Card>
                    </Col>
                </Row>
            </Col>
        </Row>

        <Row class="margin-top-10">
            <Card>
                <p slot="title" class="card-title">
                    <Icon type="ios-shuffle-strong"></Icon>
                    最近两周SQL工单量(个)
                </p>
                <div class="line-chart-con">
                    <service-requests v-if="flag" :sqlTrendChart="sqlTrendChart"></service-requests>
                </div>
            </Card>
        </Row>
        <copyright> </copyright>
    </div>
</template>

<script>
import dataSourcePie from './components/dataSourcePie.vue';
import visiteVolume from './components/visiteVolume.vue';
import serviceRequests from './components/serviceRequests.vue';
import inforCard from './components/inforCard.vue';
import toDoListItem from './components/toDoListItem.vue';
//import countUp from './components/countUp.vue';
//import userFlow from './components/userFlow.vue'
import {GetChartData} from '@/api/dashboard/chart'
import {Tag} from 'iview';
import copyright from '../my-components/public/copyright'

export default {
    name: 'home',
    components: {
        copyright,
        Tag,
        dataSourcePie,
        visiteVolume,
        serviceRequests,
        inforCard,
        toDoListItem,
        //userFlow,
        //countUp,
    },
    created() {
        this.getChartHandle()
    },
    data () {
        return {
            flag: false,
            sqlStatusChart: {},
            sqlList:[],
            userInfo:{},
            columnsSqlToday: [
                {
                    title: 'ID',
                    key: 'id',
                    width: 80,
                    render: (h, params) => {
                        return h('router-link', {props:{to:'/inceptionsql/'+params.row.id}}, params.row.id)
                    }
                },
                {
                    title: '环境',
                    key: 'env',
                    width: 80,
                    render: (h, params) => {
                        const envMap = {
                            'test':'测试',
                            'prd':'生产'
                        }
                        const env = params.row.env
                        return h('span', {}, envMap[env])
                    }
                },   
                {
                    title: '状态',
                    key: '',
                    render: (h, params) => {
                        let status = params.row.status
                        if (status == -3) {
                            return h('div', [h(Tag,{props:{}}, '已回滚')])
                        } else if (status == -2) {
                            return h('div', [h(Tag,{props:{}}, '已暂停')])
                        } else if (status == -1) {
                            return h('div', [h(Tag,{props:{color:'blue'}}, '待执行')])
                        } else if (status == 0) {
                            return h('div', [h(Tag,{props:{color:'green'}}, '已执行')])
                        } else if (status == 1) {
                            return h('div', [h(Tag,{props:{color:'yellow'}}, '已放弃')])
                        } else if (status == 2) {
                            return h('div', [h(Tag,{props:{color:'red'}}, '任务异常')])
                        }
                    }
                },
          ],
            count: {
                sql_total:0,
                sql_handled:0,
                user_total:0,
                group_total:0 
            },
            showAddNewTodo: false,
            newToDoItemValue: ''
        };
    },
    computed: {
        avatorPath () {
            return localStorage.avatorImgPath;
        },
        identity () {
            const identityMap = {
                'superuser':'管理员',
                'developer':'研发',
                'developer_manager':'经理',
                'developer_supremo':'总监'
            }
            return identityMap[this.userInfo.identity]
        },
        getDateJoined () {
            let date = this.userInfo.date_joined || ''
            return date.slice(0,19).replace('T',' ')
        }

    },
    methods: {

        getChartHandle () {
            GetChartData({})
            .then(res => {
                console.log(res)
                if (res.data.status == 0) {
                    this.count = res.data.data.count_data
                    console.log(this.count)
                    // status chart
                    this.sqlStatusChart = res.data.data.sql_status_data
                    // actionType chart
                    this.sqlTypeChart = res.data.data.sql_type_data
                    // trend Chart
                    this.sqlTrendChart = res.data.data.sql_trend_data
                    // today data
                    this.sqlList = res.data.data.sql_today_data
                    // user data
                    this.userInfo = res.data.data.user_info
                    this.flag = true 
                }

            })
            .catch(error => {
                console.log(error)
            })
      },


    }
};
</script>
