<style src="../../static/base.css"></style>

<template>
  <div>
      <Card>
      <Row>  
        <Col span="4">
          <Input icon="search" v-model="getClusterParams.search" placeholder="搜索" @on-click="handleGetClusterList" @on-enter="handleGetClusterList" />
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
          <Table :columns="columnsClusterList" :data="clusterList" size="small"></Table>
        </Col>
      </Row>
      </br>
      <Page :total=total show-sizer :current=getClusterParams.page @on-change="pageChange" @on-page-size-change="sizeChange"></Page>

    </Card>
    <copyright> </copyright>

    <Spin size="large" fix v-if="spinShow"></Spin>
    <Modal
        v-model="createModal"
        width="450"
        title="创建集群"
        @on-ok="handleCreateCluster"
        @on-cancel="cancel">
        <Form ref="createClusterForm" :model="createClusterForm" :rules="ruleCreateClusterForm" :label-width="100">
          <FormItem label="项目名：" prop="name">
            <Input v-model="createClusterForm.name"></Input>
          </FormItem>
          <FormItem label="备注：" prop="remark">
            <Input v-model="createClusterForm.remark"></Input>
          </FormItem>
        </Form>  
      </Modal>      

    <Modal
        v-model="updateModal"
        width="450"
        title="修改集群"
        @on-ok="handleUpdateCluster"
        @on-cancel="cancel">
        <Form ref="updateClusterForm" :model="updateClusterForm" :rules="ruleupdateClusterForm" :label-width="100">
          <FormItem label="项目名：" prop="name">
            <Input v-model="updateClusterForm.name"></Input>
          </FormItem>
          <FormItem label="目标数据库" prop="dbList">
            <Select v-model="updateClusterForm.dbs" multiple >
              <Option v-for="item in updateClusterForm.dbList" :value="item.id" :key="item.id">{{ item.name }}</Option>
            </Select>
          </FormItem>
          <FormItem label="备注：" prop="remark">
            <Input v-model="updateClusterForm.remark"></Input>
          </FormItem>              
        </Form>  
      </Modal>   

    <Modal
        v-model="deleteModal"
        width="450"
        title="删除集群"
        @on-ok="handleDeleteCluster"
        @on-cancel="cancel">
        <div>
          <p> 删除集群 <b>{{deleteParams.name}}</b>？</p>
          <p> (此操作只会删除集群本身，不会删除集群关联的数据库) </p>
        </div>
    </Modal>      

    <Modal
        v-model="showContent.modal"
        width="800"
        :title="showContent.title">
        <div class="modalcontent">
          <Table :columns="columnsDbList" :data="showContent.data" size="small"></Table>
        </div>
    </Modal>

  </div>
</template>
<script>
  import {Button, Table, Modal, Message, Tag} from 'iview';
  import {GetDbList} from '@/api/sql/dbs'
  import {ContainsIdList} from '@/utils/base/contains';
  import {GetClusterList, UpdateCluster, CreateCluster, DeleteCluster} from '@/api/sql/cluster'
  import copyright from '../my-components/public/copyright'

  export default {
    components: {Button, Table, Modal, Message, Tag, copyright},
    data () {
      return {
        spinShow: false,
        deleteModal: false,
        createModal: false,
        updateModal: false,
        // 显示数据库
        showContent:{
          modal:false,
          title:'',
          data:[],
        },
        search: '',
        clusterList:[],
        // 数据库配置数据
        createClusterForm: {
          name: '',
          remark:'',
        },
        ruleCreateClusterForm: {
          name: [{ required: true, message: '项目名不能为空', trigger: 'blur' }],
        },
        updateClusterForm: {
          id:'',
          name:'',
          dbs:[],
          dbList:[],
          remark:'',
        },
        ruleupdateClusterForm: {
          name: [{ required: true, message: '项目名不能为空', trigger: 'blur' }],          
        },
        columnsClusterList: [
          {
              title: '集群名',
              key: 'name'
          },
          {
              title: '数据库',
              render: (h, params) => {
                const db_ids = params.row.dbs
                let data = []
                this.dbList.map( (item) => {
                  if (ContainsIdList(db_ids, item.id) == true ){
                    data.push(item)
                  }
                })
                if (data.length == 0) {
                  var subelm = []
                } else {
                  var subelm = [
                    h(Button, {
                        props: {
                          type: 'info',
                          size: 'small'
                        },
                        style: {
                          marginRight: '12px'
                        },
                        on: {
                          click: () => {
                            this.showContent.modal = true
                            this.showContent.title = params.row.name + ' 数据库 ' + '（数量: ' + data.length + '）'
                            this.showContent.data = data
                          }
                        }
                    }, '列表')
                  ]
                }
                return h('div', {}, subelm)
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
                          this.updateClusterForm.id = row.id
                          this.updateClusterForm.name = row.name
                          this.updateClusterForm.dbs = row.dbs
                          this.updateClusterForm.dbList = this.filterDbList(this.dbList, row.dbs)
                          this.updateClusterForm.remark = row.remark
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
                        this.deleteParams.id = params.row.id
                        this.deleteParams.name = params.row.name
                      }
                    }
                  }, '删除')
                ])
              }
          },          

        ],
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
              key: 'port',
              width: 80
          },
          {
              title: '用户名',
              key: 'user',
              width: 120
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
        ],
        // delete
        deleteParams:{
          id:'',
          name:''
        },
        // get
        total:1,
        dbList:[],
        getDbParams:{
          page:1,
          pagesize:10000,
          search:'',
        },
        getClusterParams:{
          page:1,
          pagesize:10,
          search:'',
        },

      }
    },

    created (){
      this.initData()
    },

    methods: {

      initData () {
        this.handleGetClusterList()
        this.handleGetDbList()
      },

      pageChange (page) {
        this.getClusterParams.page = page
        this.initData()
      },

      sizeChange(size){
        this.getClusterParams.pagesize = size
        this.initData()
      },

      filterDbList (dbList, dbs) {
        let data = []
        dbList.map( (item) => {
          if (Object.keys(item.cluster).length === 0 || ContainsIdList(dbs, item.id) == true) {
            data.push(item)
          }
        })
        return data
      },

      handleCreateCluster () {
        this.$refs.createClusterForm.validate((valid) => {
          if (!valid) {
            return
          }
          CreateCluster(this.createClusterForm)  
          .then(
            res => {
              this.initData()
            },
          )
        })
      },

      handleUpdateCluster () {
        this.$refs.updateClusterForm.validate((valid) => {
          if (!valid) {
            return
          }
          const id = this.updateClusterForm.id 
          let data = this.updateClusterForm
          UpdateCluster(id, data)  
          .then(
            res => {
              this.initData()
            },
          )
        })
      },

      handleDeleteCluster () {
        DeleteCluster(this.deleteParams.id)
        .then(res => {
          console.log(res)
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

