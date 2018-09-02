<template>
  <div>
    <Card>
      <Alert show-icon>基本信息</Alert>
      <div style="margin-top:10px;margin-bottom:10px">

        <Row>
          <Col span="2">
            <p> <b>ID：</b> </p>
          </Col>
          <Col span="10">
            <p> {{this.$route.params.id}} </p>
          </Col>
          <Col span="2">
            <p> <b>数据库：</b>  </p>
          </Col>
          <Col span="10">
            <p> {{row.db_name}} </p>
          </Col>
        </Row>

        <Row>
          <Col span="2">
            <p> <b>提交时间：</b> </p>
          </Col>
          <Col span="10">
            <p> {{row.createtime}} </p>
          </Col>
          <Col span="2">
            <p> <b>流程：</b>  </p>
          </Col>
          <Col span="10">
            <Button size="small" @click="showStep">流程</Button> <Badge :count="badgeData.count" class-name="demo-badge-alone"></Badge>
          </Col>
        </Row>

        <Row>
          <Col span="2">
            <p> <b>提交人：</b> </p>
          </Col>
          <Col span="10">
            <p> {{row.commiter}} </p>
          </Col>
          <Col span="2">
            <p> <b>执行人：</b>  </p>
          </Col>
          <Col span="10">
            <p> {{row.treater}} </p>
          </Col>
        </Row>

        <Row>
          <Col span="2">
            <p> <b>环境：</b> </p>
          </Col>
          <Col span="10">
            <p> {{env}} </p>
          </Col>
          <Col span="2">
            <p> <b>状态：</b>  </p>
          </Col>
          <Col span="10">
            <p v-if="row.status == -3" > <Tag>已回滚</Tag> </p>
            <p v-else-if="row.status == -2" > <Tag>已暂停</Tag> </p>
            <p v-else-if="row.status == -1" > <Tag color="blue">待执行</Tag> </p>
            <p v-else-if="row.status == 0" > <Tag color="green">已执行</Tag> </p>
            <p v-else-if="row.status == 1" > <Tag color="yellow">已放弃</Tag> </p>
            <p v-else-if="row.status == 2" > <Tag color="red">执行失败</Tag> </p>
          </Col>
        </Row>
        <Row>
          <Col span="2">
            <p> <b>备注：</b> </p>
          </Col>
          <Col span="10">
            <p> {{row.remark}} </p>
          </Col>
        </Row>
      </div>
      <Alert show-icon>语句</Alert>
      <div style="margin-top:10px;margin-bottom:10px">
        <Row>
          <Col span="24">
            <Scroll height=200>
              <div v-for="(item, index) in sqlContent" :value="item.value" :key="index">{{ item.value }} </div>
            </Scroll>
          </Col>
        </Row>
      </div>
      <Alert show-icon>操作</Alert>
      <div style="margin-top:10px;margin-bottom:10px">
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
                </DropdownMenu>
                <DropdownMenu v-else-if="row.status == 0"  slot="list">
                    <DropdownItem name='rollback'>回滚</DropdownItem>
                </DropdownMenu>
            </Dropdown>
          </Col>
        </Row>
      </div>

    </Card>

    <Modal
        v-model="modalAction.show"
        width="450"
        title="SQL操作"
        @on-ok="handleAction"
        @on-cancel="cancel">
        <div>
          <center> {{ modalAction.content }} </center>
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
                <p class="content">{{ item.username }} <Tag :color="stepStatusMap[item.status]['color']" style="margin-left:10px">{{ stepStatusMap[item.status]['desc'] }}</Tag> </p>
              </TimelineItem>
            </Timeline>
          </Scroll>
        </div>
    </Modal>  

  </div>
</template>
<script>
    import {GetSqlDetail, SqlAction} from '@/api/sql/inception'
    import {getSqlContent, handleBadgeData} from '@/utils/sql/inception'
    
    export default {
      filters:{
        formatTime:function(value){
          if(value != '') {
            return value.slice(0,19).replace('T',' ')
          }
        },
      },
      data () {
        return {
          row:{},
          sqlContent:[],
          steps:[],
          stepsModal:false,
          stepStatusMap:{
            0:{color:'gray', desc:'待处理'},
            1:{color:'green', desc:'通过'},
            2:{color:'red', desc:'驳回'}
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
            rollback: {name: '回滚'}
          }
        }
      },

      created (){
        this.handleGetSqlDetail()
      },

      computed: {
        showBtn: function () {
          if (this.row.status == -3 || this.row.status == 1) {
            return false
          } else {
            return true
          }
        }, 
        env: function () {
          if (this.row.env == 'prd') {
            return '生产'
          } else if (this.row.env == 'test') {
            return '测试'
          }
        },

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
              let desc = h('p', {}, '信息：' + msg) 
              let subtags = [id, desc]
              return h('div', subtags)
            }
          });
        },

        showAction (name) {
          this.modalAction.id = this.row.id
          this.modalAction.action = name
          this.modalAction.show = true
          this.modalAction.content = this.descMap[name].name + ' 此工单?'
        },

        handleAction () {
          let id = this.modalAction.id
          let action = this.modalAction.action
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
              }
              this.handleGetSqlDetail()
            } else {
              let msg = response.data.msg
              this.alertWarning('执行失败', id, msg)
            } 
          })
        },

        handleGetSqlDetail () {
            GetSqlDetail(this.$route.params.id)
            .then(response => {
              console.log(response)
              this.row = response.data
              this.steps = this.row.steps
              this.sqlContent = getSqlContent(this.row.sql_content)
              this.badgeData = handleBadgeData(this.steps)
            })
        },

      }
    }    
</script>