<template>
  <div>
      <Card>
      <Row>  
        <Col span="4">
          <Input icon="search" v-model="getParams.search" placeholder="搜索" @on-click="handleGetDbList" @on-enter="handleGetDbList" />
        </Col>

        <Col span="10">
          <center>
            <Button type="primary" @click='createModal = true'>创建</Button>
          </center>
        </Col>
      </Row>
      </br>
      <Row>
        <Col span="22">
          <Table :columns="columnsDbList" :data="dbList" size="small"></Table>
        </Col>
      </Row>
      </br>
      <Page :total=total show-sizer :current=getParams.page @on-change="pageChange" @on-page-size-change="sizeChange"></Page>

    </Card>
    <Spin size="large" fix v-if="spinShow"></Spin>
    <Modal
        v-model="createModal"
        width="450"
        title="创建数据库配置"
        @on-ok="handleCreateDb"
        @on-cancel="cancel">
        <Form ref="createDbForm" :model="createDbForm" :rules="ruleCreateDbForm" :label-width="100">
          <FormItem label="环境：" prop="env">
            <Select v-model="createDbForm.env">
              <Option value="prd" >生产</Option>
              <Option value="test" >测试</Option>
            </Select>
          </FormItem>
          <FormItem label="数据库名：" prop="name">
            <Input v-model="createDbForm.name"></Input>
          </FormItem>
          <FormItem label="地址：" prop="host">
            <Input v-model="createDbForm.host"></Input>
          </FormItem>
          <FormItem label="端口：" prop="port">
            <Input v-model="createDbForm.port"></Input>
          </FormItem>
          <FormItem label="用户名：" prop="user">
            <Input v-model="createDbForm.user"></Input>
          </FormItem>
          <FormItem label="密码：" prop="password">
            <Input v-model="createDbForm.password" type="password"></Input>
          </FormItem>
          <FormItem label="备注：" prop="remark">
            <Input v-model="createDbForm.remark"></Input>
          </FormItem>              
        </Form>  
      </Modal>      

    <Modal
        v-model="updateModal"
        width="450"
        title="修改数据库配置"
        @on-ok="handleUpdateDb"
        @on-cancel="cancel">
        <Form ref="updateDbForm" :model="updateDbForm" :rules="ruleupdateDbForm" :label-width="100">
          <FormItem label="环境：">
            <Select v-model="updateDbForm.env">
              <Option value="prd" >生产</Option>
              <Option value="test" >测试</Option>
            </Select>
          </FormItem>
          <FormItem label="数据库名：" prop="name">
            <Input v-model="updateDbForm.name"></Input>
          </FormItem>
          <FormItem label="地址：" prop="host">
            <Input v-model="updateDbForm.host"></Input>
          </FormItem>
          <FormItem label="端口：" prop="port">
            <Input v-model="updateDbForm.port"></Input>
          </FormItem>
          <FormItem label="用户名：" prop="user">
            <Input v-model="updateDbForm.user"></Input>
          </FormItem>
          <FormItem label="密码：" prop="password">
            <Input v-model="updateDbForm.password" type="password"></Input>
          </FormItem>
          <FormItem label="备注：" prop="remark">
            <Input v-model="updateDbForm.remark"></Input>
          </FormItem>              
        </Form>  
      </Modal>   

    <Modal
        v-model="deleteModal"
        width="450"
        title="删除数据库配置"
        @on-ok="handleDeleteDb"
        @on-cancel="cancel">
        <div>
          <p> 删除数据库配置 <b>{{dbName}}</b> ？</p>
        </div>
    </Modal>      

  </div>
</template>
<script>
  import {Button, Table, Modal, Message, Tag} from 'iview';
  import {GetDbList, UpdateDb, CreateDb, DeleteDb} from '@/api/sql/dbs'

  export default {
    components: {Button, Table, Modal, Message, Tag},
    data () {
      return {
        spinShow: false,
        deleteModal: false,
        createModal: false,
        updateModal: false,
        search: '',
        // 数据库配置数据
        createDbForm: {
          env: 'prd',
          name: '',
          host:'',
          port:'',
          user:'',
          password:'',
          remark:'',
        },
        ruleCreateDbForm: {
          name: [{ required: true, message: '数据库名不能为空', trigger: 'blur' }],
          host: [{ required: true, message: '数据库地址不能为空', trigger: 'blur' }],
          port: [{ required: true, message: '数据库端口不能为空', trigger: 'blur' }],
          user: [{ required: true, message: '用户名不能为空', trigger: 'blur' }],
          password: [{ required: true, message: '密码不能为空', trigger: 'blur' }],
        },
        updateDbForm: {
          id:'',
          env: '',
          name: '',
          host:'',
          port:'',
          user:'',
          password:'',
          remark:'',
        },
        ruleupdateDbForm: {
          name: [{ required: true, message: '数据库名不能为空', trigger: 'blur' }],
          host: [{ required: true, message: '数据库地址不能为空', trigger: 'blur' }],
          port: [{ required: true, message: '数据库端口不能为空', trigger: 'blur' }],
          user: [{ required: true, message: '用户名不能为空', trigger: 'blur' }],
          password: [{ required: true, message: '密码不能为空', trigger: 'blur' }],
        },
        columnsDbList: [
          {
              title: '数据库名',
              key: 'name'
          },
          {
              title: '数据库地址',
              key: 'host'
          },
          {
              title: '端口',
              key: 'port'
          },
          {
              title: '用户名',
              key: 'user'
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
              title: '备注',
              key: 'remark'
          },
          {
              title: '操作',
              key: 'action',
              width: 150,
              align: 'center',
              render: (h, params) => {
                return h('div', [
                  h(Button, {
                      props: {
                        type: 'primary',
                        size: 'small'
                      },
                      style: {
                        marginRight: '12px'
                      },
                      on: {
                        click: () => {
                          console.log(params.row)
                          this.updateModal = true
                          //this.updateDbForm = params.row
                          this.updateDbForm.id = params.row.id
                          this.updateDbForm.env = params.row.env
                          this.updateDbForm.name = params.row.name
                          this.updateDbForm.host = params.row.host
                          this.updateDbForm.port = params.row.port
                          this.updateDbForm.user = params.row.user
                          this.updateDbForm.password = params.row.password
                          this.updateDbForm.remark = params.row.remark
                        }
                      }
                  }, '修改'),
                  h(Button, {
                    props: {
                      type: 'error',
                      size: 'small'
                    },
                    on: {
                      click: () => {
                        this.deleteModal = true
                        this.deleteId = params.row.id
                        this.dbName = params.row.name
                      }
                    }
                  }, '删除')
                ])
              }
          },          

        ],
        // delete
        deleteId:'',
        dbName:'',
        // get
        total:1,
        dbList:[],
        getParams:{
          page:1,
          pagesize:10,
          search:'',
        }
      }
    },

    created (){
      this.handleGetDbList()
    },

    methods: {

      pageChange (page) {
        this.getParams.page = page
        this.handleGetDbList()
      },

      sizeChange(size){
        this.getParams.pagesize = size
        this.handleGetDbList()
      },

      handleCreateDb () {
        this.$refs.createDbForm.validate((valid) => {
          if (!valid) {
            return
          }
          CreateDb(this.createDbForm)  
          .then(
            res => {
              this.handleGetDbList()
            },
          )
        })
      },

      handleUpdateDb () {
        this.$refs.updateDbForm.validate((valid) => {
          if (!valid) {
            return
          }
          const id = this.updateDbForm.id 
          let data = this.updateDbForm
          delete data._index
          delete data._rowKey
          UpdateDb(id, data)  
          .then(
            res => {
              this.handleGetDbList()
            },
          )
        })
      },

      handleDeleteDb () {
        DeleteDb(this.deleteId)
        .then(res => {
          console.log(res)
          this.handleGetDbList()
        })
        .catch(error => {
          console.log(error)
        })
      },
     
      handleGetDbList () {
        this.spinShow = true
        GetDbList(this.getParams)
        .then(
          res => {
            this.spinShow = false
            this.dbList = res.data.results
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

