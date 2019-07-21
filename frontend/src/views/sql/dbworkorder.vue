<style src="../../static/base.css"></style>

<template>
  <div>
      <Card>
      <Row>  
        <Col span="4">
          <Input icon="search" v-model="getMinParams.search" placeholder="搜索" @on-click="handleGetList" @on-enter="handleGetList" />
        </Col>

        <Col span="10">
          <center>
            <Button type="primary" @click='createModal = true'>创建</Button>
          </center>
        </Col>
      </Row>
      </br>
      <Row>
        <Col span="23">
          <Table :columns="columnsDbWorkOrderList" :data="dbWorkOrderList" size="small"></Table>
        </Col>
      </Row>
      </br>
      <Page :total=total show-sizer :current=getMinParams.page @on-change="pageChange" @on-page-size-change="sizeChange"></Page>

    </Card>
    <copyright> </copyright>

    <Spin size="large" fix v-if="spinShow"></Spin>
    <Modal
        v-model="createModal"
        width="450"
        title="创建数据库工单"
        @on-ok="handleCreateDbWorkOrder">
        <Form ref="createDbWorkOrderForm" :model="createDbWorkOrderForm" :rules="ruleCreateDbWorkOrderForm" :label-width="100">
          <FormItem label="所属集群：" prop="db_cluster">
            <Select v-model="createDbWorkOrderForm.db_cluster" filterable>
              <Option v-for="item in clusterList" :value="item.id" :key="item.id">{{ item.name }}</Option>
            </Select>
          </FormItem>
          <FormItem label="环境：">
            <Select v-model="createDbWorkOrderForm.env">
              <Option value="prd" >生产</Option>
              <Option value="test" >测试</Option>
            </Select>
          </FormItem>
          <FormItem label="主机：" prop="db_host">
            <Input v-model="createDbWorkOrderForm.db_host"></Input>
          </FormItem>
          <FormItem label="端口：" prop="db_port">
            <Input v-model="createDbWorkOrderForm.db_port"></Input>
          </FormItem>
          <FormItem label="数据库" prop="db_list">
            <Input v-model="createDbWorkOrderForm.db_list" type="textarea" :autosize="{minRows: 2,maxRows: 2}" placeholder="多个数据库以空格分隔" />
          </FormItem>
          <FormItem label="备注" prop="remark">
            <Input v-model="createDbWorkOrderForm.remark" type="textarea" :autosize="{minRows: 2,maxRows: 2}" placeholder="请输入备注" />
          </FormItem>
        </Form>  
      </Modal>      

    <Modal
        v-model="updateModal"
        width="450"
        title="修改数据库工单"
        @on-ok="handleUpdateWorkOrder">
        <Form ref="updateDbWorkOrderForm" :model="updateDbWorkOrderForm" :rules="ruleUpdateDbWorkOrderForm" :label-width="100">
          <FormItem label="所属集群：" prop="db_cluster">
            <Select v-model="updateDbWorkOrderForm.db_cluster" filterable>
              <Option v-for="item in clusterList" :value="item.id" :key="item.id">{{ item.name }}</Option>
            </Select>
          </FormItem>
          <FormItem label="环境：">
            <Select v-model="updateDbWorkOrderForm.env">
              <Option value="prd" >生产</Option>
              <Option value="test" >测试</Option>
            </Select>
          </FormItem>
          <FormItem label="主机：" prop="db_host">
            <Input v-model="updateDbWorkOrderForm.db_host"></Input>
          </FormItem>
          <FormItem label="端口：" prop="db_port">
            <Input v-model="updateDbWorkOrderForm.db_port"></Input>
          </FormItem>
          <FormItem label="数据库" prop="db_list">
            <Input v-model="updateDbWorkOrderForm.db_list" type="textarea" :autosize="{minRows: 2,maxRows: 2}" placeholder="多个数据库以空格分隔" />
          </FormItem>
          <FormItem label="备注" prop="remark">
            <Input v-model="updateDbWorkOrderForm.remark" type="textarea" :autosize="{minRows: 2,maxRows: 2}" placeholder="请输入备注" />
          </FormItem>
        </Form>  
    </Modal>   

    <Modal
        v-model="modalAction.show"
        width="450"
        title="工单操作"
        @on-ok="handleAction">
        <div>
          <center> {{actionMap[actionData.status]}}  工单 (ID:{{actionData.id}}) </center>
        </div>
    </Modal>  

    <Modal
        v-model="deleteModal"
        width="450"
        title="删除集群"
        @on-ok="handleDeleteDbWorkOrder"
        @on-cancel="cancel">
        <div>
          <p> 删除集群 <b>{{deleteParams.name}}</b>？</p>
          <p> (此操作只会删除集群本身，不会删除集群关联的数据库) </p>
        </div>
    </Modal>      

  </div>
</template>
<script>
  import {Button, Table, Modal, Message, Tag, DropdownItem, Dropdown, DropdownMenu, Icon} from 'iview';
  import {GetDbWorkOrderList, CreateDbWorkOrder, ManageDbWorkOrder, UpdateDbWorkOrder} from '@/api/sql/dbworkorder'
  import {formatTime} from '@/utils/base/date'
  import {GetClusterList} from '@/api/sql/cluster'
  import copyright from '../my-components/public/copyright'

  export default {
    components: {Button, Table, Modal, Message, Tag, copyright},
    data () {
      return {
        spinShow:false,
        deleteModal:false,
        createModal:false,
        updateModal:false,
        modalAction:{
          show:false
        },
        // 显示数据库
        showContent:{
          modal:false,
          title:'',
          data:[],
        },
        search: '',
        clusterList:[],
        dbWorkOrderList:[],
        // 数据库配置数据
        createDbWorkOrderForm: {
          db_cluster:'',
          b_env:'prd',
          db_host:'',
          db_port:'',
          db_list:''
        },
        ruleCreateDbWorkOrderForm: {
          name: [{ required: true, message: '项目名不能为空', trigger: 'blur' }],
        },
        updateDbWorkOrderForm: {
          id:'',
          env:'',
          db_cluster:'',
          db_host:'',
          db_port:'',
          db_list:''
        },
        actionMap: {
          1:'审核通过',
          2:'审核驳回',
          3:'放弃'
        },
        actionData: {
          id:'',
          status:''
        },
        ruleUpdateDbWorkOrderForm: {
          name: [{ required: true, message: '项目名不能为空', trigger: 'blur' }],          
        },
        columnsDbWorkOrderList: [
          {
            title: 'ID',
            key: 'id',
            width: 60
          },
          {
            title: '提交人',
            key: 'commiter'
          },
          {
            title: '提交时间',
            key: 'createtime',
            render: (h, params) => {
              let time = params.row.createtime
              return h('div', {}, [                 
                formatTime(time)
              ])
            }
          },
          {
            title: '配置详情',
            render: (h, params) => {
              return h('div', {}, [
                h(Button, {
                    props: {
                      type: 'warning',
                      size: 'small'
                    },
                    style: {
                      marginRight: '12px'
                    },
                    on: {
                      click: () => {
                        const row = params.row
                        this.updateModal = true
                        this.updateDbWorkOrderForm.id = row.id
                        this.updateDbWorkOrderForm.db_cluster = row.db_cluster
                        this.updateDbWorkOrderForm.env = row.env
                        this.updateDbWorkOrderForm.db_host = row.db_host
                        this.updateDbWorkOrderForm.db_port = row.db_port
                        this.updateDbWorkOrderForm.db_list = row.db_list

                      }
                    }
                }, '编辑')
              ])
            }
          },
          {
            title: '审核人',
            key: 'treater'
          },
          {
            title: '审核时间',
            key: 'updatetime',
            render: (h, params) => {
              let time = ''
              let status = params.row.status
              if (status == 1 || status == 2){
                time = formatTime(params.row.updatetime)
              }
              return h('div', {}, [                 
                time
              ])
            }
          },
          {
            title: '工单状态',
            width: 120,
            render: (h, params) => {
              let status = params.row.status
              if (status == 0) {
                return h('div', [h(Tag, {props:{color:'blue'}}, '待审核')])
              } else if (status == 1) {
                return h('div', [h(Tag, {props:{color:'green'}}, '审核通过')])
              }  else if (status == 2) {
                return h('div', [h(Tag, {props:{color:'red'}}, '审核驳回')])
              }  else if (status == 3) {
                return h('div', [h(Tag, {}, '已放弃')])
              } 
            }
          },
          {
            title: '操作',
            width: 100,
            render: (h, params) => {
              let id = params.row.id
              var ddItem = [
                  h(DropdownItem, {nativeOn:{click: () => {this.manageAction(id, 1)}}}, ['审核通过']),
                  h(DropdownItem, {nativeOn:{click: () => {this.manageAction(id, 2)}}}, ['审核驳回']),
                  h(DropdownItem, {nativeOn:{click: () => {this.manageAction(id, 3)}}}, ['放弃']),
              ]
              return h('div', {}, [
                  h(Dropdown,
                  {
                      props:{
                          style: {marginLeft: '20px'},
                      }
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
          }
        ],
        // delete
        deleteParams:{
          id:'',
          name:''
        },
        // get
        total:1,
        dbList:[],
        getMaxParams:{
          page:1,
          pagesize:10000,
          search:'',
        },
        getMinParams:{
          page:1,
          pagesize:10,
          search:'',
        },

      }
    },

    created (){
      this.handleGetClusterList()
      this.initData()
    },

    methods: {

      initData () {
        this.handleGetList()
      },

      pageChange (page) {
        this.getMinParams.page = page
        this.initData()
      },

      sizeChange(size){
        this.getMinParams.pagesize = size
        this.initData()
      },
      alertSuccess (title, paramId) {
        this.$Notice.success({
          title: title,
          duration: 6,
          render: h => {
            let id = h('p', {}, 'ID：' + paramId) 
            let subtags = [id]
            return h('div', subtags)
          }
        });
      },

      manageAction (id, status) {
        this.modalAction.show = true
        this.actionData.id = id
        this.actionData.status = status
      },

      handleGetClusterList () {
        this.spinShow = true
        GetClusterList(this.getMaxParams)
        .then(
          res => {
            this.spinShow = false
            this.clusterList = res.data.results
          }
        )
      },
      handleAction () {
        ManageDbWorkOrder(this.actionData)
        .then(
          res => {
            let httpStatus = res.status
            if (httpStatus == 200){
              this.alertSuccess(this.actionMap[this.actionData.status], this.actionData.id)
            }
            this.initData()
          },
        )        
      },
      handleCreateDbWorkOrder () {
        this.$refs.createDbWorkOrderForm.validate((valid) => {
          if (!valid) {
            return
          }
          CreateDbWorkOrder(this.createDbWorkOrderForm)  
          .then(
            res => {
              this.initData()
            },
          )
        })
      },

      handleUpdateWorkOrder () {
        this.$refs.updateDbWorkOrderForm.validate((valid) => {
          if (!valid) {
            return
          }
          const id = this.updateDbWorkOrderForm.id 
          let data = this.updateDbWorkOrderForm
          console.log(this.updateDbWorkOrderForm)
          UpdateDbWorkOrder(id, data)  
          .then(
            res => {
              this.initData()
            },
          )
        })
      },

      handleDeleteDbWorkOrder () {
        DeleteDbWorkOrder(this.deleteParams.id)
        .then(res => {
          console.log(res)


          this.initData()
        })
      },
     
      handleGetList () {
        this.spinShow = true
        GetDbWorkOrderList(this.getMinParams)
        .then(
          res => {
            console.log(res)
            this.spinShow = false
            this.dbWorkOrderList = res.data.results
            this.total = res.data.count
          }
        )
      },

      cancel () {
        Message.info('Clicked cancel');
      }


    },


  }
</script>

