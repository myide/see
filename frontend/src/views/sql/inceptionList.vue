<style scoped>
    .time{
        font-size: 14px;
        font-weight: bold;
    }
    .content{
        padding-left: 5px;
    }
</style>

<template>
    <div>
        <div>
          <Card>
            <Row>
              <Col span="4">
                <Input icon="search" v-model="getParams.search" placeholder="搜索" @on-click="handleGetSqlList" @on-enter="handleGetSqlList" />
              </Col>
              <Col span="6">
                <DatePicker type="daterange" :options="dateOption" @on-change="dateChange" @on-clear="dateClear" placement="bottom-end" placeholder="选择日期范围" style="width: 200px; float:right"></DatePicker>
              </Col>
            </Row>  
            </br>
            <Row>
              <Table :columns="columnsSqlList" :data="sqlList"></Table>
              </br>
              <Page :total=total show-sizer :current=getParams.page @on-change="pageChange" @on-page-size-change="sizeChange"></Page>
            </Row>
          </Card>
        </div>
        <Spin size="large" fix v-if="spinShow"></Spin>
        <Modal
            v-model="sqlContentModal"
            width="650"
            title="SQL语句"
            @on-cancel="cancel">
            <div>
              <Scroll height=450>
                <div v-for="(item, index) in sqlContent" :value="item.value" :key="index">{{ item.value }} </div>
              </Scroll>
            </div>
        </Modal>  

        <Modal
            v-model="stepsModal"
            width="400"
            :title="stepsModalTitle"
            @on-cancel="cancel">
            <div>
              <Scroll height=450>
                <Timeline>
                  <TimelineItem v-for="(item, index) in steps" :value="item.value" :key="index" :color="getColor(item.status)">
                    <p class="time">{{ item.updatetime | formatTime }}</p>
                    <p class="content">{{ item.username }} <Tag :color="stepStatusMap[item.status]['color']" style="margin-left:10px">{{ stepStatusMap[item.status]['desc'] }}</Tag> </p>
                  </TimelineItem>
                </Timeline>
              </Scroll>
            </div>
        </Modal>  

     </div>
</template>
<script>
  import {GetStrategyList} from '@/api/sql/strategy'
  import {GetSqlList, SqlAction} from '@/api/sql/inception'
  import {getSqlContent} from '@/utils/sql/inception'
  import {addDate} from '@/utils/base/date'
  import {handleBadgeData} from '@/utils/sql/inception'
  import baseData from '@/utils/sql/data'

  import {Button, Table, Page, Modal, Message, Icon, Tag, DropdownMenu, DropdownItem, Dropdown, Tooltip, Poptip, Badge} from 'iview';

  export default {
    components: {Button, Table, Page, Modal, Message, Icon, Tag, DropdownMenu, DropdownItem, Dropdown, Tooltip, Poptip, Badge},
    filters:{
      formatTime:function(value){
        if(value != '') {
          return value.slice(0,19).replace('T',' ')
        }
      },
    },
    computed:{

    },
    data () {
      return {
        spinShow:false,
        steps:[],
        stepsModal:false,
        stepsModalTitle:'',
        stepStatusMap:{
          0:{color:'gray', desc:'待处理'},
          1:{color:'green', desc:'通过'},
          2:{color:'red', desc:'驳回'}
        },
        strategy:{is_manual_review:false},
        total:1,
        getParams:{
          page:1,
          pagesize:10,
          search:'',
          daterange:''
        },
        sqlContent:[],
        sqlContentModal: false,
        sqlList:[],
        dateOption:baseData.dateOption,
        columnsSqlList: [
          {
            title: 'ID',
            key: 'id',
            width: 60,
            render: (h, params) => {
              return h('router-link', {props:{to:'/inceptionsql/'+params.row.id}}, params.row.id)
            }
          },

          {
            title: '提交时间',
            key: '',
            width: 150,
            render: (h, params) => {
              return h('div', [
                h('span', {}, params.row.createtime.split('.')[0].replace('T',' ')),
              ])
            }
          },

          {
            title: '提交人',
            key: 'commiter'
          },

          {
            title: '环境',
            key: 'env',
            width: 120,
            render: (h, params) => {
              const envMap = {
                'test':{color:'gray', desc:'测试'},
                'prd':{color:'orange', desc:'生产'}
              }
              const env = params.row.env
              return h(Tag, {props:{type:'dot', color:envMap[env]['color']}}, envMap[env]['desc'])
            }
          },

          {
            title: '数据库',
            key: 'db_name',
          },

          {
            title: 'SQL语句',
            key: '',
            width: 220,
            render: (h, params) => {
              return h('div', [
                h('span', {}, params.row.sql_content.slice(0,20) + '...'),
                h('Button', {
                  props: {
                    size: 'small',
                  },
                  style: {float:'right'},
                  on: {
                    click: () => {
                      this.sqlContent = getSqlContent(params.row.sql_content)
                      this.sqlContentModal = true
                    }
                  }
                }, '语句')
              ])
            }
          },

          {
            title: '流程',
            key: '',
            render: (h, params) => {
              const statusMap = {
                1:'success',
                2:'warning'
              }
              const steps = params.row.steps
              let badgeData = handleBadgeData(steps)
              if (steps.length > 0) {
                var subElement = 
                [
                  h(Button, {
                      props: {
                        size: 'small',
                        ghost: true
                      },
                      style: {},
                      on: {
                        click: () => {
                          this.stepsModalTitle = '工单流程' + '（ID: ' + params.row.id + '）'
                          this.steps = steps
                          this.stepsModal = true
                        }
                      }
                    }, '流程'),
                  h(Badge, {props:{count:badgeData.count, type:statusMap[badgeData.badgeStatus] }},[])
                ]

              } else {
                subElement = []
              }
              return h('div', {}, subElement)
            }
          },

          {
            title: '备注',
            key: 'remark',
            render: (h, params) => {
              let remark = params.row.remark
              if (remark.length >= 6){
                var abbreviatedRemark = params.row.remark.slice(0,6) + '...'
              } else {
                var abbreviatedRemark = remark
              }
              // return h('span',{attrs:{title: remark}}, abbreviatedRemark)
              return h(Tooltip,{props:{placement: "top", content: remark}}, 
              [
                h('div', {props:{slot:'content'}}, [h('div',{}, abbreviatedRemark)])
              ])

            }
          },

          {
            title: '操作状态',
            key: '',
            width: 100,
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
                return h('div', [h(Tag,{props:{color:'red'}}, '执行失败')])
              }

            }
          },

          {
            title: '执行人',
            key: 'treater'
          },
          
          {
            title: '操作',
            key: 'action',
            width: 150,
            align: 'center',
            render: (h, params) => {
              const id = params.row.id
              let status = params.row.status
              let popcss = {
                width:170,
                place:'top',
              }
              
              if (status == -1){
                var ddItem = [ 
                  h('div' , {}, [h(Poptip,{props:{confirm:true, placement:popcss.place, width:popcss.width, transfer:true, title:'执行 此工单(' + id + ') ？'}, on:{'on-ok': () => {this.handleAction('execute', params)} } }, [h(DropdownItem, {}, '执行')] ) ]) , 
                  h('div' , {}, [h(Poptip,{props:{confirm:true, placement:popcss.place, width:popcss.place, transfer:true, title:'放弃 此工单(' + id + ') ？'}, on:{'on-ok': () => {this.handleAction('reject', params)} } }, [h(DropdownItem, {}, '放弃')] ) ]),
                  h('div' , {style:{display: this.strategy.is_manual_review != true || status == -2 ? 'none' : 'display'}}, [h(Poptip,{props:{confirm:true, placement:popcss.place, width:popcss.place, transfer:true, title:'审批通过 此工单(' + id + ') ？'}, on:{'on-ok': () => {this.handleAction('approve', params)} } }, [h(DropdownItem, {}, '审批通过')] ) ]),
                  h('div' , {style:{display: this.strategy.is_manual_review != true || status == -2 ? 'none' : 'display'}}, [h(Poptip,{props:{confirm:true, placement:popcss.place, width:popcss.place, transfer:true, title:'审批驳回 此工单(' + id + ') ？'}, on:{'on-ok': () => {this.handleAction('disapprove', params)} } }, [h(DropdownItem, {}, '审批驳回')] ) ]),
                ]
              } else if (status == 0){
                var ddItem = [ h(Poptip,{props:{confirm:true, placement:popcss.place, width:popcss.width, transfer:true, title:'回滚 此工单(' + id + ') ？'}, on:{'on-ok': () => {this.handleAction('rollback', params)} } }, [h(DropdownItem, {}, '回滚')] ) ]
              } else {
                var ddItem = []
              }
              return h('div', {style:{display: status == -3 || status == 1 ? 'none' : 'display'}}, [
                h(Dropdown,
                {
                  style: {marginLeft: '20px'},
                },
                [
                  h(Button, {props:{type: 'primary', size: 'small'}}, [h('span', {style:{marginRight: '1px'}}, '操作'), h(Icon, {props:{type: 'arrow-down-b'}})], ),
                  h(DropdownMenu, 
                    {
                      slot: 'list',
                    }, 
                    ddItem               
                  )
                ], ),
              ])
            }
          },

        ],

      }
    },

    created () {
      this.handleGetSqlList()
      this.handleGetStrategyList()
    },

    methods: {
      getColor(status){
        return this.stepStatusMap[status]['color']
      },

      alertSuccess (title, sqlid, execute_time, affected_rows) {
        this.$Notice.success({
          title: title,
          render: h => {
            let id = h('p', {}, 'ID：' + sqlid) 
            let time = execute_time ? h('p', {}, '耗时（秒）：' + execute_time) : ''
            let rows = affected_rows ? h('p', {}, '影响的行数：' + affected_rows) : ''
            let subtags = [id, time, rows]
            return h('div', subtags)
          }
        });
      },

      alertWarning (title, sqlid, msg) {
        this.$Notice.warning({
          title: title,
          duration: 0,
          render: h => {
            let id = h('p', {}, 'ID：' + sqlid) 
            let desc = h('p', {}, 'Msg：' + msg) 
            let subTags = [id, desc]
            return h('div', subTags)
          }
        });
      },

      getDatetime () {
        let date = this.userInfo.date_joined || ''
        return date.slice(0,19).replace('T',' ')
      },

      handleGetSqlList () {
        this.spinShow = true
        GetSqlList(this.getParams)
        .then(response => {
          this.spinShow = false
          this.sqlList = response.data.results
          this.total = response.data.count
        })
      },

      handleAction (action, params) {
        let id = params.row.id
        SqlAction(id, action)
        .then(response => {
          console.log(response)
          const status = response.data.status
          const data = response.data.data
          if (status == 0) {
            if (action == 'execute') {
              this.alertSuccess('执行成功', id, data.execute_time, data.affected_rows)
            } else if (action == 'rollback') {
              this.alertSuccess('回滚成功', id, '', data.affected_rows)
            } else if (action == 'approve') {
              this.alertSuccess('审批通过', id, '')
            } else if (action == 'disapprove') {
              this.alertSuccess('审批驳回', id, '')
            }
          } else {
            let msg = response.data.msg
            this.alertWarning('任务失败', id, msg)
          } 
          this.handleGetSqlList()
        })
      },

      handleGetStrategyList () {
        GetStrategyList({})
        .then(
          response => {
            console.log(response)
            const results = response.data.results
            if (results) {
              this.strategy = results[0]
              console.log(this.strategy.is_manual_review == false)
            }
          }
        )
      },

      cancel () {
        Message.info('Clicked cancel');
      },

      pageChange (page) {
        this.getParams.page = page
        this.handleGetSqlList()
      },

      sizeChange(size){
        this.getParams.pagesize = size
        this.handleGetSqlList()
      },

      dateChange (data) {
        console.log(data)
        if (data[0]) {
          this.getParams.daterange = data[0] + ',' + addDate(data[1], 1)
          this.handleGetSqlList()
        }
      },

      dateClear (data) {
        console.log(data)
      }

    },
  }
</script>
