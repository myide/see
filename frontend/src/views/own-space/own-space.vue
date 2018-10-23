<style lang="less">
    @import './own-space.less';
</style>

<template>
    <div>
        <Card>
            <p slot="title">
                <Icon type="person"></Icon>
                个人信息
            </p>
            <div>
                <Form 
                    ref="userForm"
                    :model="userForm" 
                    :label-width="100" 
                    label-position="right"
                >
                    <FormItem label="用户名：">
                        <div style="display:inline-block;width:300px;">
                            <p> {{ userForm.username }}</p>
                        </div>
                    </FormItem>

                    <FormItem label="加入时间：">
                        <div style="display:inline-block;width:300px;">
                            <p> {{ userForm.date_joined }}</p>
                        </div>
                    </FormItem>

                    <FormItem label="Email：">
                        <div style="display:inline-block;width:300px;">
                            <p> {{ userForm.email }}</p>
                        </div>
                    </FormItem>

                    <FormItem label="登录密码：">
                        <Button type="text" size="small" @click="showEditPassword">修改密码</Button>
                    </FormItem>
                </Form>
            </div>
        </Card>
        <Modal v-model="editPasswordModal" :closable='false' :mask-closable=false :width="500">
            <h3 slot="header" style="color:#2D8CF0">修改密码</h3>
            <Form ref="editPasswordForm" :model="editPasswordForm" :label-width="100" label-position="right" :rules="passwordValidate">
                <FormItem label="原密码" prop="old_pass" :error="oldPassError">
                    <Input v-model="editPasswordForm.old_pass" placeholder="请输入现在使用的密码" ></Input>
                </FormItem>
                <FormItem label="新密码" prop="new_pass">
                    <Input v-model="editPasswordForm.new_pass" placeholder="请输入新密码，至少6位字符" ></Input>
                </FormItem>
                <FormItem label="确认新密码" prop="rep_pass">
                    <Input v-model="editPasswordForm.rep_pass" placeholder="请再次输入新密码" ></Input>
                </FormItem>
            </Form>
            <div slot="footer">
                <Button type="text" @click="cancelEditPass">取消</Button>
                <Button type="primary" :loading="savePassLoading" @click="saveEditPass">保存</Button>
            </div>
        </Modal>
    </div>
</template>

<script>
import { GetPersonal, UpdatePersonal } from '@/api/account/account'

export default {
    name: 'ownspace_index',
    data () {
        const validePhone = (rule, value, callback) => {
            var re = /^1[0-9]{10}$/;
            if (!re.test(value)) {
                callback(new Error('请输入正确格式的手机号'));
            } else {
                callback();
            }
        };
        const valideRePassword = (rule, value, callback) => {
            if (value !== this.editPasswordForm.new_pass) {
                callback(new Error('两次输入密码不一致'));
            } else {
                callback();
            }
        };
        return {
            userForm: {
                username: 'Terry',
            },
            uid: '', // 登录用户的userId
            securityCode: '', // 验证码
            phoneHasChanged: false, // 是否编辑了手机
            save_loading: false,
            identifyError: '', // 验证码错误
            editPasswordModal: false, // 修改密码模态框显示
            savePassLoading: false,
            oldPassError: '',
            identifyCodeRight: false, // 验证码是否正确
            hasGetIdentifyCode: false, // 是否点了获取验证码
            canGetIdentifyCode: false, // 是否可点获取验证码
            checkIdentifyCodeLoading: false,
            editPasswordForm: {
                old_pass: '',
                new_pass: '',
                rep_pass: ''
            },
            passwordValidate: {
                old_pass: [
                    { required: true, message: '请输入原密码', trigger: 'blur' }
                ],
                new_pass: [
                    { required: true, message: '请输入新密码', trigger: 'blur' },
                    { min: 6, message: '请至少输入6个字符', trigger: 'blur' },
                    { max: 32, message: '最多输入32个字符', trigger: 'blur' }
                ],
                rep_pass: [
                    { required: true, message: '请再次输入新密码', trigger: 'blur' },
                    { validator: valideRePassword, trigger: 'blur' }
                ]
            },
            inputCodeVisible: false, // 显示填写验证码box
            initPhone: '',
            gettingIdentifyCodeBtnContent: '获取验证码' // “获取验证码”按钮的文字
        };
    },
    methods: {
        getIdentifyCode () {
            this.hasGetIdentifyCode = true;
            this.$refs['userForm'].validate((valid) => {
                if (valid) {
                    this.canGetIdentifyCode = true;
                    let timeLast = 60;
                    let timer = setInterval(() => {
                        if (timeLast >= 0) {
                            this.gettingIdentifyCodeBtnContent = timeLast + '秒后重试';
                            timeLast -= 1;
                        } else {
                            clearInterval(timer);
                            this.gettingIdentifyCodeBtnContent = '获取验证码';
                            this.canGetIdentifyCode = false;
                        }
                    }, 1000);
                    this.inputCodeVisible = true;
                    // you can write ajax request here
                }
            });
        },
        showEditPassword () {
            this.editPasswordModal = true;
        },
        cancelEditUserInfor () {
            this.$store.commit('removeTag', 'ownspace_index');
            localStorage.pageOpenedList = JSON.stringify(this.$store.state.app.pageOpenedList);
            let lastPageName = '';
            if (this.$store.state.app.pageOpenedList.length > 1) {
                lastPageName = this.$store.state.app.pageOpenedList[1].name;
            } else {
                lastPageName = this.$store.state.app.pageOpenedList[0].name;
            }
            this.$router.push({
                name: lastPageName
            });
        },
        saveEdit () {
            this.$refs['userForm'].validate((valid) => {
                if (valid) {
                    if (this.phoneHasChanged && this.userForm.cellphone !== this.initPhone) { // 手机号码修改过了而且修改之后的手机号和原来的不一样
                        if (this.hasGetIdentifyCode) { // 判断是否点了获取验证码
                            if (this.identifyCodeRight) { // 判断验证码是否正确
                                this.saveInfoAjax();
                            } else {
                                this.$Message.error('验证码错误，请重新输入');
                            }
                        } else {
                            this.$Message.warning('请先点击获取验证码');
                        }
                    } else {
                        this.saveInfoAjax();
                    }
                }
            });
        },
        cancelEditPass () {
            this.editPasswordModal = false;
        },
        getPersonal () {
            GetPersonal()
            .then(response => {
                console.log(response)
                this.userForm = response.data
            })
        },
        saveEditPass () {
            this.$refs['editPasswordForm'].validate((valid) => {
                if (valid) {
                    // you can write ajax request here
                    UpdatePersonal(this.editPasswordForm)
                    .then(response => {
                        console.log(response)
                        this.$Message.success('保存成功');
                        this.editPasswordModal = false
                    })
                };
            })
        },
        init () {
            this.userForm.name = 'Lison';
            this.userForm.cellphone = '17712345678';
            this.initPhone = '17712345678';
            this.userForm.company = 'TalkingData';
            this.userForm.department = '可视化部门';
        },
        cancelInputCodeBox () {
            this.inputCodeVisible = false;
            this.userForm.cellphone = this.initPhone;
        },
        submitCode () {
            let vm = this;
            vm.checkIdentifyCodeLoading = true;
            if (this.securityCode.length === 0) {
                this.$Message.error('请填写短信验证码');
            } else {
                setTimeout(() => {
                    this.$Message.success('验证码正确');
                    this.inputCodeVisible = false;
                    this.checkIdentifyCodeLoading = false;
                }, 1000);
            }
        },
        hasChangePhone () {
            this.phoneHasChanged = true;
            this.hasGetIdentifyCode = false;
            this.identifyCodeRight = false;
        },
        saveInfoAjax () {
            this.save_loading = true;
            setTimeout(() => {
                this.$Message.success('保存成功');
                this.save_loading = false;
            }, 1000);
        }
    },
    mounted () {
        this.init();
        this.getPersonal()
    }
};
</script>
