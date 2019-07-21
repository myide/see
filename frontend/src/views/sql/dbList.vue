<template>
  <div>
      <Card>
      <Row>  
        <Col span="4">
          <Input icon="search" v-model="getDbParams.search" placeholder="搜索" @on-click="handleGetDbList" @on-enter="handleGetDbList" />
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
          <Table :columns="columnsDbList" :data="dbList" size="small"></Table>
        </Col>
      </Row>
      </br>
      <Page :total=total show-sizer :current=getDbParams.page @on-change="pageChange" @on-page-size-change="sizeChange"></Page>

    </Card>
    <copyright> </copyright>

    <Spin size="large" fix v-if="spinShow"></Spin>
    <Modal
        v-model="createModal"
        width="800"
        title="创建数据库配置"
        @on-ok="handleCreateDb"
        @on-cancel="cancel">
        <div>
          <Row>
            <Col span="12">
              <Form ref="createDbForm" :model="createDbForm" :rules="ruleCreateDbForm" :label-width="100">
                <FormItem label="所属集群：" prop="cluster">
                  <Select v-model="createDbForm.cluster" filterable @on-change="clearDatabases">
                    <Option v-for="item in clusterList" :value="item.id" :key="item.id">{{ item.name }}</Option>
                  </Select>
                </FormItem>
                <FormItem label="环境：" prop="env">
                  <Select v-model="createDbForm.env">
                    <Option value="prd">生产</Option>
                    <Option value="test">测试</Option>
                  </Select>
                </FormItem>
                <FormItem label="地址：" prop="host">
                  <Input v-model="createDbForm.host" placeholder="mysql地址"></Input>
                </FormItem>
                <FormItem label="端口：" prop="port">
                  <Input v-model="createDbForm.port" placeholder="mysql端口"></Input>
                </FormItem>
                <FormItem label="用户名：" prop="user">
                  <Input v-model="createDbForm.user" placeholder="mysql用户名"></Input>
                </FormItem>
                <FormItem label="密码：" prop="password">
                  <Input v-model="createDbForm.password" type="password" placeholder="mysql密码"></Input>
                </FormItem>
                <FormItem label="获取数据库">
                  <Button type="info" shape="circle" @click="createCheckConn">连接</Button>
                </FormItem>             
              </Form>
            </Col>
            
            <Col span="12">
              <Form ref="createDbForm" :model="createDbForm" :rules="ruleCreateDbForm" :label-width="100">
                <FormItem label="数据库：" prop="cluster">
                  <div style="border-bottom: 1px solid #e9e9e9;padding-bottom:6px;margin-bottom:6px;">
                    <Checkbox
                      :indeterminate="indeterminate"
                      :value="checkAll"
                      @click.prevent.native="handleCheckAll">全选</Checkbox>
                  </div>
                  <div style="height:300px;overflow-x:auto">
                    <CheckboxGroup v-model="databases" @on-change="checkAllGroupChange">
                      <Checkbox v-for="item in databaseList" :value="item" :key="item" :label="item"></Checkbox>
                    </CheckboxGroup>
                  </div>
                </FormItem>
              </Form>
            </Col>
            
          </Row>
        </div>
    </Modal>      

    <Modal
        v-model="updateModal"
        width="450"
        title="修改数据库配置"
        @on-ok="handleUpdateDb"
        @on-cancel="cancel">
        <Form ref="updateDbForm" :model="updateDbForm" :rules="ruleupdateDbForm" :label-width="100">
          <FormItem label="所属集群：" prop="cluster">
            <Select v-model="updateDbForm.cluster" filterable>
              <Option v-for="item in clusterList" :value="item.id" :key="item.id">{{ item.name }}</Option>
            </Select>
          </FormItem>
          <FormItem label="环境：">
            <Select v-model="updateDbForm.env">
              <Option value="prd" >生产</Option>
              <Option value="test" >测试</Option>
            </Select>
          </FormItem>
          <FormItem label="地址：" prop="host">
            <Input v-model="updateDbForm.host" placeholder="mysql地址"></Input>
          </FormItem>
          <FormItem label="端口：" prop="port">
            <Input v-model="updateDbForm.port" placeholder="mysql端口"></Input>
          </FormItem>
          <FormItem label="用户名：" prop="user">
            <Input v-model="updateDbForm.user" placeholder="mysql用户名"></Input>
          </FormItem>
          <FormItem label="密码：" prop="password">
            <Input v-model="updateDbForm.password" type="password" placeholder="mysql密码"></Input>
          </FormItem>
          <FormItem label="库名：" prop="name">
            <Input v-model="updateDbForm.name" placeholder="mysql实际的库名"></Input>
          </FormItem>
          <FormItem label="备注：" prop="remark">
            <Input v-model="updateDbForm.remark"></Input>
          </FormItem>     
          <FormItem label="连接测试">
              <Button type="info" shape="circle" @click="updateCheckConn">连接</Button>
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
          <div v-if="permission_relate == 1">
            <p> 数据库 <b>{{dbName}}</b> 已关联用户/组，是否继续删除 </p>
          </div>
          <div v-else>
            <p> 删除数据库配置 <b>{{dbName}}</b> ？ </p>
          </div>
        </div>
    </Modal>      

  </div>
</template>
<script>
  import {Button, Table, Modal, Message, Tag} from 'iview';
  import {GetTableRelatedStatus} from '@/api/sql/sqlquery'
  import {GetDbList, UpdateDb, CreateDb, DeleteDb, CheckConn, GetDatabases} from '@/api/sql/dbs'
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
        search:'',
        // 待选择的数据库
        indeterminate: true,
        checkAll: false,
        // get permission relate
        permission_relate:'',
        // 数据库配置数据
        databaseList:[],
        databases:[],
        createDbForm: {
          cluster:'',
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
          cluster:'',
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
            title: '所属集群',
            render: (h, params) => {
              const clusterName = params.row.cluster.name
              return h('div', {}, clusterName)
            }
          },
          {
            title: '数据库地址',
            key: 'host',
            width: 130,
          },
          {
            title: '端口',
            key: 'port',
            width: 80,
          },
          {
            title: '用户名',
            key: 'user',
            width: 120,
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
                          const row = params.row
                          this.updateModal = true
                          this.updateDbForm.cluster = row.cluster.id
                          this.updateDbForm.id = row.id
                          this.updateDbForm.env = row.env
                          this.updateDbForm.name = row.name
                          this.updateDbForm.host = row.host
                          this.updateDbForm.port = row.port
                          this.updateDbForm.user = row.user
                          this.updateDbForm.password = row.password
                          this.updateDbForm.remark = row.remark
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
                        this.getPermissionRelate(params.row.id)
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
        clusterList:[],
        getDbParams:{
          page:1,
          pagesize:10,
          search:'',
        },
        getClusterParams:{
          page:1,
          pagesize:10000,
          search:'',
        },
      }
    },

    created (){
      this.initData()
    },

    methods: {

      clearDatabases () {
        this.databases = []
      },

      handleCheckAll () {
        if (this.indeterminate) {
          this.checkAll = false;
        } else {
          this.checkAll = !this.checkAll;
        }
        this.indeterminate = false;
        if (this.checkAll) {
          this.databases = this.databaseList;
        } else {
          this.databases = [];
        }
      },

      checkAllGroupChange (data) {
        if (data.length === this.databaseList.length) {
          this.indeterminate = false;
          this.checkAll = true;
        } else if (data.length > 0) {
          this.indeterminate = true;
          this.checkAll = false;
        } else {
          this.indeterminate = false;
          this.checkAll = false;
        }
      },

      initData () {
        this.handleGetClusterList()
        this.handleGetDbList()
      },

      pageChange (page) {
        this.getDbParams.page = page
        this.initData()
      },

      sizeChange (size){
        this.getDbParams.pagesize = size
        this.initData()
      },

      getPermissionRelate (id) {
        GetTableRelatedStatus (id)
        .then(
          res => {
            this.permission_relate = res.data.results
          })
      },

      createCheckConn () {
        this.$refs.createDbForm.validate((valid) => {
          if (!valid) {
            return
          }
          const data = {
            //check_type: 'create_target_db',
            cluster: this.createDbForm.cluster,
            env: this.createDbForm.env,            
            host: this.createDbForm.host,
            port: this.createDbForm.port,
            user: this.createDbForm.user,
            password: this.createDbForm.password,
          }
          GetDatabases(data)
          .then(
          res => {
            this.databaseList = res.data.data
          })
        })
      },

      updateCheckConn () {
        const data = {
          check_type: 'update_target_db',
          id: this.updateDbForm.id
        }
        this.handleCheckConn(data)
      },

      handleCheckConn (data) {
        CheckConn(data)
        .then(
          res => {
            const status = res.data.status
            const data = res.data.data
            if (status == 0) {
                this.$Message.success(
                    {
                        content:'连接成功',
                        duration: 3
                    }
                )
            } else {
                this.$Message.warning(
                    {
                        content:'连接失败 （' + data + '）',
                        duration: 8
                    }
                )
            }
          })
      },

      handleCreateDb () {
        this.$refs.createDbForm.validate((valid) => {
          if (!valid) {
            return
          }
          let data = []
          for (let dbName of this.databases) {
            //let item = this.createDbForm
            let item = {}
            item.name = dbName
            item.env = this.createDbForm.env
            item.cluster = this.createDbForm.cluster
            item.host = this.createDbForm.host
            item.port = this.createDbForm.port
            item.user = this.createDbForm.user
            item.password = this.createDbForm.password            
            data.push(item)
          }
          CreateDb(data)  
          .then(
            res => {
              this.initData()
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
              this.initData()
            },
          )
        })
      },

      handleDeleteDb () {
        DeleteDb(this.deleteId)
        .then(res => {
          this.initData()
        })
      },
     
      handleGetDbList () {
        this.spinShow = true
        GetDbList(this.getDbParams)
        .then(
          res => {
            this.spinShow = false
            this.dbList = res.data.results
            this.total = res.data.count
          }
        )
      },

      handleGetClusterList () {
        this.spinShow = true
        GetClusterList(this.getClusterParams)
        .then(
          res => {
            this.spinShow = false
            this.clusterList = res.data.results
          }
        )
      },

      cancel () {
        Message.info('Clicked cancel');
      }

    },


  }
</script>

