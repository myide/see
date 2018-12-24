<style scoped>
    .inner {
      margin-top:20px
    }
</style>

<template>
  <div>
    <Card>
      <div>
        <Tabs size="small">
          <TabPane label="基本信息"><baseInfo v-if="flag" :row="row"> </baseInfo></TabPane>
          <TabPane label="SQL语句"><sqlContentInfo v-if="flag" :sqlContent="sqlContent"> </sqlContentInfo></TabPane>
          <TabPane :label="labelResult"><handleResult v-if="flag" :row="row" :handleResultCheck="handle_result_check" :handleResultExecute="handle_result_execute" :handleResultRollback="handle_result_rollback" > </handleResult></TabPane>
          <TabPane :label="suggestionLabel" name="suggestion"><suggestionInfo @refreshList="handleGetList" :id="this.$route.params.id" :res="res"> </suggestionInfo></TabPane>
        </Tabs>
      </div>
      <div class="inner" v-if="is_has_flow(row)">
        <p></p>
        <Alert show-icon>工单流</Alert>
        <Steps :current="stepCurrent" :status="stepCurrentStatus">
          <step v-for="(item, index) in stepList" :title="item.title" :content="item.content" :key="index"> </step>
        </Steps>
      </div>
      <div class="inner">
        <p></p>
        <Alert show-icon>操作</Alert>
        <Row>
          <Col span="24">
            <Dropdown v-show="showBtn" @on-click='showAction'>
              <Button type="primary">
                操作
                <Icon type="arrow-down-b"></Icon>
              </Button>
              <DropdownMenu v-if="row.status == -1"  slot="list">
                <DropdownItem name='execute'>执行</DropdownItem>
                <DropdownItem name='reject'>放弃</DropdownItem>
                <DropdownItem name='approve' v-if="showItem">审批通过</DropdownItem>
                <DropdownItem name='disapprove' v-if="showItem">审批驳回</DropdownItem>
              </DropdownMenu>
              <DropdownMenu v-else-if="row.status == 0"  slot="list">
                <DropdownItem name='rollback'>回滚</DropdownItem>
              </DropdownMenu>
            </Dropdown>
          </Col>
        </Row>
      </div>

    </Card>
    <copyRight> </copyRight>

    <Modal
        v-model="modalAction.show"
        width="450"
        title="SQL操作"
        @on-ok="handleAction"
        @on-cancel="cancel">
        <div>
          <center> {{modalAction.content}} </center>
        </div>
    </Modal>  

    <Modal
        v-model="stepsModal"
        width="400"
        title="流程"
        @on-cancel="cancel">
        <div>
          <Scroll height=450>
            <Timeline>
              <TimelineItem v-for="(item, index) in steps" :value="item.value" :key="index" :color="getColor(item.status)">
                <p class="time">{{ item.updatetime | formatTime }}</p>
                <p class="content">{{item.username}} <Tag :color="stepStatusMap[item.status]['color']" style="margin-left:10px">{{ stepStatusMap[item.status]['desc'] }}</Tag> </p>
              </TimelineItem>
            </Timeline>
          </Scroll>
        </div>
    </Modal>  

  </div>
</template>

<script>
    import {GetSuggestionList} from '@/api/sql/suggestion'
    import {GetSqlDetail, SqlAction} from '@/api/sql/inception'
    import {getSqlContent, handleBadgeData} from '@/utils/sql/inception'
    import copyRight from '../my-components/public/copyright'
    import baseInfo from './components/baseInfo'
    import sqlContentInfo from './components/sqlContentInfo'
    import handleResult from './components/handleResult'
    import suggestionInfo from './components/suggestionInfo'

    export default {
      components: {copyRight, baseInfo, sqlContentInfo, handleResult, suggestionInfo},
      filters:{
        formatTime:function(value){
          if(value != '') {
            return value.slice(0,19).replace('T',' ')
          }
        },
      },
      data () {
        return {
          flag:false,
          stepList:[],
          stepCurrent:0,
          stepCurrentStatus:'finish',
          res:{},
          count:'',
          suggestionLabel:(h) => {
            return h('div', [
              h('span', '审批意见'),
              h('Badge', {
                props: {
                  count: this.count
                }
              })
            ])
          },
          row:{},
          handle_result_check:[],
          handle_result_execute:[],
          handle_result_rollback:[],
          sqlContent:[],
          steps:[],
          stepsModal:false,
          stepStatusMap:{
            '-1':{color:'gray', desc:'终止', stepStatus:'wait'},
            0:{color:'gray', desc:'待处理', stepStatus:'wait'},
            1:{color:'green', desc:'通过', stepStatus:'finish'}, 
            2:{color:'red', desc:'驳回', stepStatus:'error'},
            3:{color:'red', desc:'放弃', stepStatus:'error'}
          },
          badgeData:{count:'', badgeStatus:''},
          modalAction: 
          {
            show:false,
            id:'',
            action:'',
            content:'',
          },
          descMap:{
            execute: {name: '执行'},
            reject: {name: '放弃'},
            rollback: {name: '回滚'},
            approve: {name: '审批通过'},
            disapprove: {name: '审批驳回'}
          }
        }
      },

      created () {
        this.handleGetSqlDetail()
      },

      computed: {
        showBtn: function () {
          if (this.row.status == -4 || this.row.status == -3 || this.row.status == 1 || (this.row.type == 'select' && this.row.status == 0 ) || this.row.rollback_able == 0 ) {
            return false
          } else {
            return true
          }
        }, 
        showItem: function () {
          const row = this.row
          if (row.is_manual_review == true && row.env == 'prd' && row.status != -2 && row.handleable == false) {
            return true
          } else {
            return false
          }
        },
        env: function () {
          if (this.row.env == 'prd') {
            return '生产'
          } else if (this.row.env == 'test') {
            return '测试'
          }
        },
        labelResult: function () {
          if (this.row.type == 'select') {
            return '查询结果' 
          } else {
            return 'Inception结果'
          }
        }

      },

      methods: {

        cancel () {
          this.$Message.info('Clicked cancel');
        },

        showStep () {
          this.stepsModal = true
        },

        getColor(status){
          return this.stepStatusMap[status]['color']
        },

        is_has_flow (row) {
          const env = row.env
          const is_manual_review = row.is_manual_review
          if (env == 'prd' && is_manual_review == true) {
            return true
          } else {
            return false
          }
        },

        handleGetList (page) {
          const params = {page:page, pagesize:10, work_order_id:this.$route.params.id}
          GetSuggestionList(params)
          .then(
            response => {
              console.log(response)
              this.res = response
              this.count = response.data.count
            }
          )
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

        showAction (name) {
          this.modalAction.id = this.row.id
          this.modalAction.action = name
          this.modalAction.show = true
          this.modalAction.content = this.descMap[name].name + ' 工单?'
        },

        getStepData () {
          if (this.is_has_flow(this.row) == false ) {
            return false
          }
          let current = -1
          this.stepList = []
          for (let i in this.steps) {
            const item = this.steps[i]
            const statusCode = item.status
            if (statusCode != 0 && statusCode != -1) {
              current += 1
            }

            const desc = ' [' + this.stepStatusMap[statusCode]['desc'] + '] '
            const dateTime = item.updatetime.split('.')[0].replace('T',' ')
            this.stepList.push(
              {
                title: item.group,
                content: item.username + desc + dateTime
              }
            )
          }
          this.stepCurrent = current
          let currentStatus = this.steps[current].status 
          this.stepCurrentStatus = this.stepStatusMap[currentStatus]['stepStatus']  // 数字转换成组件状态
        },

        parseHandleResult(handle_result){
          console.log(handle_result, typeof(handle_result))
          if (handle_result == "") {
            return
          }
          const data = JSON.parse(handle_result)
          let ret = []
          for (let i in data){
            ret.push(
              {
                value:JSON.stringify(data[i])
              }
            )
            
          }
          return ret
        },

        handleAction () {
          let id = this.modalAction.id
          let action = this.modalAction.action
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
                this.alertSuccess('审批通过', id, '', '')
              } else if (action == 'disapprove') {
                this.alertSuccess('审批驳回', id, '', '')
              } 
              this.handleGetSqlDetail()
            } else {
              let msg = response.data.msg
              this.alertWarning('任务失败', id)
            } 
          })
        },

        handleGetSqlDetail () {
          GetSqlDetail(this.$route.params.id)
          .then(response => {
            console.log(response)
            this.row = response.data
            this.steps = this.row.steps
            this.handle_result_check = this.parseHandleResult(this.row.handle_result_check)
            this.handle_result_execute = this.parseHandleResult(this.row.handle_result_execute)
            this.handle_result_rollback = this.parseHandleResult(this.row.handle_result_rollback)
            this.sqlContent = getSqlContent(this.row.sql_content)
            this.badgeData = handleBadgeData(this.steps)
            this.handleGetList(1)
            this.getStepData()
            this.flag = true
          })
        },

      }
    }    
</script>