<style scoped>
  .time{
    font-size: 14px;
  }
  .content{
    font-weight: bold;
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
              <Table :columns="columnsSqlList" :data="sqlList" size="small"></Table>
              </br>
              <Page :total=total show-sizer :current=getParams.page @on-change="pageChange" @on-page-size-change="sizeChange"></Page>
            </Row>
          </Card>
          <copyright> </copyright>
        </div>
        <Spin size="large" fix v-if="spinShow"></Spin>
        <Modal
            v-model="sqlContentModal"
            width="650"
            :title="sqlContentTitle"
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
                    <p class="content">{{ item.username }}  </p>
                    <p class="time">{{ item.updatetime | formatTime }} <Tag :color="stepStatusMap[item.status]['color']" style="margin-left:10px">{{ stepStatusMap[item.status]['desc'] }}</Tag></p>
                  </TimelineItem>
                </Timeline>
              </Scroll>
            </div>
        </Modal>  

     </div>
</template>
<script>
  import {GetSqlList, SqlAction} from '@/api/sql/inception'
  import {getSqlContent} from '@/utils/sql/inception'
  import {addDate} from '@/utils/base/date'
  import {handleBadgeData} from '@/utils/sql/inception'
  import baseData from '@/utils/sql/data'
  import copyright from '../my-components/public/copyright'
  import {Button, Table, Page, Modal, Message, Icon, Tag, DropdownMenu, DropdownItem, Dropdown, Tooltip, Poptip, Badge} from 'iview';

  export default {
    components: {Button, Table, Page, Modal, Message, Icon, Tag, DropdownMenu, DropdownItem, Dropdown, Tooltip, Poptip, Badge, copyright},
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
          '-1':{color:'gray', desc:'终止', stepStatus:'wait'},
          0:{color:'gray', desc:'待处理'},
          1:{color:'green', desc:'通过'},
          2:{color:'red', desc:'驳回'},
          3:{color:'red', desc:'放弃'}
        },
        total:1,
        getParams:{
          page:1,
          pagesize:10,
          search:'',
          daterange:''
        },
        sqlContentTitle:'',
        sqlContent:[],
        sqlContentModal: false,
        sqlList:[],
        dateOption:baseData.dateOption,
        columnsSqlList: [
          {
            title: 'ID',
            width: 60,
            render: (h, params) => {
              return h('router-link', {props:{to:'/inceptionsql/'+params.row.id}}, params.row.id)
            }
          },

          {
            title: '提交时间',
            width: 150,
            render: (h, params) => {
              return h('div', [
                h('span', {}, params.row.createtime.split('.')[0].replace('T',' ')),
              ])
            }
          },

          {
            title: '发起人',
            key: 'commiter'
          },

          {
            title: '环境',
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
            title: '目标库',
            key: 'db_name',
          },

          {
            title: 'SQL语句',
            width: 150,
            render: (h, params) => {
              return h('div', [
                h('span', {}, params.row.sql_content.slice(0,6) + '...'),
                h('Button', {
                  props: {
                    size: 'small',
                  },
                  style: {float:'right'},
                  on: {
                    click: () => {
                      this.sqlContent = getSqlContent(params.row.sql_content)
                      this.sqlContentModal = true
                      this.sqlContentTitle = 'SQL语句' + '（工单ID: ' + params.row.id + '）'
                    }
                  }
                }, '语句')
              ])
            }
          },

          {
            title: '流程',
            width: 100,
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
            width: 100,
            render: (h, params) => {
              let remark = params.row.remark
              if (remark.length >= 6){
                var abbreviatedRemark = params.row.remark.slice(0,4) + '...'
              } else {
                var abbreviatedRemark = remark
              }
              return h(Tooltip,{props:{placement: "top", content: remark}}, 
              [
                h('div', {props:{slot:'content'}}, [h('div',{}, abbreviatedRemark)])
              ])

            }
          },

          {
            title: '工单状态',
            width: 120,
            render: (h, params) => {
              let status = params.row.status
              if (status == -4) {
                return h('div', [h(Tag,{props:{color:'red'}}, '回滚失败')])
              } else if (status == -3) {
                return h('div', [h(Tag,{props:{}}, '已回滚')])
              } else if (status == -2) {
                return h('div', [h(Tag,{props:{}}, '已暂停')])
              } else if (status == -1) {
                return h('div', [h(Tag,{props:{color:'blue'}}, '待执行')])
              } else if (status == 0) {
                return h('div', [h(Tag,{props:{color:'green'}}, '成功')])
              } else if (status == 1) {
                return h('div', [h(Tag,{props:{color:'yellow'}}, '已放弃')])
              } else if (status == 2) {
                return h('div', [h(Tag,{props:{color:'red'}}, '任务失败')])
              } 
            }
          },

          {
            title: '核准人',
            key: 'treater'
          },
          
          {
            title: '操作',
            width: 150,
            align: 'center',
            render: (h, params) => {
              const id = params.row.id
              const status = params.row.status
              const rollbackable = params.row.rollback_able
              const type = params.row.type
              const handleable = params.row.handleable
              const is_manual_review = params.row.is_manual_review
              let popcss = {
                width:170,
                place:'top',
              }
              if (status == -1) {
                var ddItem = [ 
                  h('div' , {}, [h(Poptip,{props:{confirm:true, placement:popcss.place, width:popcss.width, transfer:true, title:'执行 工单(' + id + ') ？'}, on:{'on-ok': () => {this.handleAction('execute', params)} } }, [h(DropdownItem, {}, '执行')] ) ]) , 
                  h('div' , {}, [h(Poptip,{props:{confirm:true, placement:popcss.place, width:popcss.place, transfer:true, title:'放弃 工单(' + id + ') ？'}, on:{'on-ok': () => {this.handleAction('reject', params)} } }, [h(DropdownItem, {}, '放弃')] ) ]),
                  h('div' , {style:{display: is_manual_review == false || handleable == true  || status == -2 ? 'none' : 'display'}}, [h(Poptip,{props:{confirm:true, placement:popcss.place, width:popcss.place, transfer:true, title:'审批通过 工单(' + id + ') ？'}, on:{'on-ok': () => {this.handleAction('approve', params)} } }, [h(DropdownItem, {}, '审批通过')] ) ]),
                  h('div' , {style:{display: is_manual_review == false || handleable == true  || status == -2 ? 'none' : 'display'}}, [h(Poptip,{props:{confirm:true, placement:popcss.place, width:popcss.place, transfer:true, title:'审批驳回 工单(' + id + ') ？'}, on:{'on-ok': () => {this.handleAction('disapprove', params)} } }, [h(DropdownItem, {}, '审批驳回')] ) ]),
                ]
              } else if (status == 0){
                var ddItem = [ h(Poptip,{props:{confirm:true, placement:popcss.place, width:popcss.width, transfer:true, title:'回滚 工单(' + id + ') ？'}, on:{'on-ok': () => {this.handleAction('rollback', params)} } }, [h(DropdownItem, {}, '回滚')] ) ]
              } else {
                var ddItem = []
              }
              return h('div', {style:{display: status == -4 || status == -3 || status == 1 || (status == 0 && type == 'select') || (status == 0 && rollbackable == 0) ? 'none' : 'display'}}, [
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
    },

    methods: {
      getColor(status){
        return this.stepStatusMap[status]['color']
      },

      alertSuccess (title, paramId, execute_time, affected_rows) {
        this.$Notice.success({
          title: title,
          render: h => {
            let id = h('p', {}, 'ID：' + paramId) 
            let time = execute_time ? h('p', {}, '耗时（秒）：' + execute_time) : ''
            let rows = affected_rows ? h('p', {}, '影响的行数：' + affected_rows) : ''
            let subtags = [id, time, rows]
            return h('div', subtags)
          }
        });
      },

      alertWarning (title, paramId) {
        this.$Notice.warning({
          title: title,
          duration: 0,
          render: h => {
            let id = h('p', {}, 'ID：' + paramId) 
            let desc = h('p', {}, '具体查看工单详情[inception结果]') 
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
            this.alertWarning('任务失败', id)
          } 
          this.handleGetSqlList()
        })
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
