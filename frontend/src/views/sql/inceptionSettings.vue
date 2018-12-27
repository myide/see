<style scoped>
    .inner {
        margin-bottom: 10px;
        margin-left: 10px;
    }

</style>

<template>
    <div>
        <Row>            
            <Col span="8">
                <Card>
                    <Alert show-icon>inception连接</Alert>
                    <div style="height:510px">
                        <Tabs>
                            <TabPane label="inception服务">
                                <Form ref="inceptionForm" :model="inceptionForm" :rules="ruleInceptionForm" :label-width="100">
                                    <FormItem label="地址：" prop="host">
                                        <Input v-model="inceptionForm.host" :readonly="readonly"></Input>
                                    </FormItem>
                                    <FormItem label="端口：" prop="port">
                                        <Input v-model="inceptionForm.port" :readonly="readonly"></Input>
                                    </FormItem>      
                                    <FormItem label="操作">
                                        <div>
                                            <Button type="warning" v-show="readonly == true" @click="editHandle">编辑</Button>
                                            <Button type="primary" v-show="readonly == false" @click="saveHandle">保存</Button>
                                        </div>
                                    </FormItem>
                                    <FormItem label="连接测试">
                                        <Button type="info" shape="circle" @click="checkInceptionConn">连接</Button>
                                    </FormItem>                                           
                                    <FormItem>
                                        <div style="color:#7B7B7B;">(上次变更时间：{{time}})</div>
                                    </FormItem>
                                </Form>  
                            </TabPane>
                            <TabPane label="inception备份库">
                                <Form ref="inceptionBackup" :model="inceptionBackup" :label-width="100">
                                    <FormItem label="地址：">
                                        <div>{{inceptionBackup.inception_remote_backup_host}}</div>
                                    </FormItem>
                                    <FormItem label="端口：">
                                        <div>{{inceptionBackup.inception_remote_backup_port}}</div>
                                    </FormItem>  
                                    <FormItem label="用户名：">
                                        <div>{{inceptionBackup.inception_remote_system_user}}</div>
                                    </FormItem>
                                    <FormItem label="密码：">
                                        <div>{{inceptionBackup.inception_remote_system_password}}</div>
                                    </FormItem>
                                    <FormItem label="连接测试">
                                        <Button type="info" shape="circle" @click="checkBackupConn">连接</Button>
                                    </FormItem>
                                </Form>  
                            </TabPane>
                        </Tabs>
                    </div>
                </Card>
            </Col>
            <Col span="16">
                <Card>
                    <div class="inner">
                        <Alert show-icon>inception变量</Alert>
                        <Scroll height=500>
                            <Table :columns="columnsInception" :data="inceptionVariables"></Table>
                        </Scroll>
                    </div>
                </Card>
            </Col>
        </Row>
        <copyright> </copyright>
    </div>
</template>
<script>
    import {GetInceptionVariables, CheckConn, SetInceptionVariables, GetInceptionBackup, GetInceptionConnection, CreateInceptionConnection, UpdateInceptionConnection} from '@/api/sql/inceptionSettings'
    import copyright from '../my-components/public/copyright'

    export default {
        components:{copyright},
        data () {
            return {
                readonly:true,
                time:'',
                valueMap: {
                    ON:true,
                    OFF:false,
                },
                getDbParams:{
                    page:1,
                    pagesize:1000,
                    search:'',
                },
                inceptionForm: {
                    id:'',
                    host:'',
                    port:'',
                    updatetime:''
                },
                inceptionBackup:{
                    inception_remote_backup_host:'',
                    inception_remote_backup_port:'',
                    inception_remote_system_user:'',
                    inception_remote_system_password:''
                },
                ruleInceptionForm: {
                    host: [{ required: true, message: 'Inception地址不能为空', trigger: 'blur' }],
                    port: [{ required: true, message: 'Inception端口不能为空', trigger: 'blur' }],
                },
                inceptionVariables:[],
                columnsInception: [
                    {
                        title: '参数名字',
                        render: (h, params) => {
                            return h('Tag', {}, params.row.name)
                        }
                    },
                    {
                        title: '可选参数',
                        key: 'param',
                        width: 100
                    },
                    {
                        title: '默认值',
                        key: 'default',
                        width: 80
                    },
                    {
                        title: '功能说明',
                        key: 'instructions',
                        render: (h, params) => {
                            let instructions = params.row.instructions
                            if (instructions.length >= 20) {
                                let instructions = instructions
                            }
                            return h('div', {}, instructions)
                        }
                    },
                    {
                        title: '设置',
                        width: 80,
                        render: (h, params) => {
                            const name = params.row.name
                            const value = params.row.value
                            const bool_value = this.valueMap[value]
                            return h('i-switch', {             
                                props: {                      
                                    size: 'large',                    
                                    value: bool_value,
                                },                                                
                                on: {                                             
                                    'on-change': (e) => {   
                                        if (e) {
                                            var valueTag = 'ON'
                                        } else {
                                            valueTag = 'OFF'
                                        }                  
                                        const data = {
                                            variable_name: name,
                                            variable_value: valueTag
                                        }
                                        this.handleSetInceptionVariables(data)              
                                    }                                               
                                }                                                 
                            }, [                                                
                                h('span', {                                       
                                    slot: 'open',                                   
                                    domProps: {                                     
                                        innerHTML: 'ON'                               
                                    }                                               
                                }),                                               
                                h('span', {                                       
                                    slot: 'close',                                  
                                    domProps: {                                     
                                        innerHTML: 'OFF'                               
                                    }                                               
                                })                                                
                            ]) 
                        }
                    }

                ],


            }
        },

        created () {
            this.handleGetInceptionBackup()
            this.handleGetInceptionVariables()
            this.handleGetInceptionConnection()
        },

        methods: {

            editHandle () {
                this.readonly = false
            },
            
            saveHandle () {
                this.readonly = true
                this.handleWriteConf()
            },

            getUpdatetime () {
                let time = this.inceptionForm.updatetime
                if (time != '') {
                    this.time = time.split('.')[0].replace('T',' ')
                }
            },

            variablesNotice (title, name, value) {
                this.$Notice.success({
                    title: title,
                    duration: 6,
                    render: h => {
                        return h('div', [
                            '参数 ' + name,
                            h('p', '的值设置为 '),
                                value
                        ])
                    }
                });
            },

            notice (title, msg) {
                this.$Notice.success({
                title: title,
                duration: 6,
                desc: msg
                });
            },

            handleNotice (response) {
                let httpstatus = response.status
                if (httpstatus == 200 || httpstatus == 201) {
                    let title = '服务器提示'
                    let msg = '设置 保存成功'
                    this.notice(title, msg)
                }
            },

            checkInceptionConn () {
                const data = {
                    check_type: 'inception_conn',
                }
                this.HandleCheckConn(data)
            },

            checkBackupConn () {
                const data = {
                    check_type: 'inception_backup',
                    host: this.inceptionBackup.inception_remote_backup_host,
                    port: this.inceptionBackup.inception_remote_backup_port,
                    user: this.inceptionBackup.inception_remote_system_user,
                }
                this.HandleCheckConn(data)
            },

            handleWriteConf () {
                const id = this.inceptionForm.id 
                const data = this.inceptionForm
                if (id == '') {
                    CreateInceptionConnection (data)  
                    .then(
                        response => {
                            this.handleNotice(response)
                            this.handleGetInceptionConnection()
                        },
                    )
                } else {
                    UpdateInceptionConnection (id, data)  
                    .then(
                        response => {
                            this.handleNotice(response)
                            this.handleGetInceptionConnection()
                        },
                    )
                }
            },

            handleGetInceptionVariables () {
                GetInceptionVariables(this.getDbParams)
                .then(res => {
                    console.log(res)
                    this.inceptionVariables = res.data.results
                })
            },

            handleSetInceptionVariables (data) {
                SetInceptionVariables(data)
                .then(res => {
                    const status = res.data.status
                    if (status == 0) {
                        let title = '服务器提示'
                        this.variablesNotice(title, data.variable_name, data.variable_value)
                    }
                })
            },

            HandleCheckConn (data) {
                CheckConn(data)
                .then(res => {
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

            handleGetInceptionConnection () {
                GetInceptionConnection()
                .then(res => {
                    console.log(res)
                    let results = res.data.results
                    if (results.length > 0) {
                        this.inceptionForm = results[0]
                        this.getUpdatetime()
                    }
                })
            },

            handleGetInceptionBackup () {
                GetInceptionBackup()
                .then(res => {
                    console.log(res)
                    this.inceptionBackup = res.data.data       
                })
            },

         
        }

    }
</script>