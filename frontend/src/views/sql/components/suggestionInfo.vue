<style scoped>
    .inner {
        margin-bottom:10px
    }
</style>

<template>
    <div>
      <div>
        <Row>
          <Col span="16">
            <Scroll height=280>
              <div>
                <Table :columns="columnsSuggestion" :data="results" :show-header="showHeader"></Table>
              </div>
              <div>
                <p></p>
                <Page :total=count :current=page @on-change="pageChange" size="small" show-total></Page>
              </div>
            </Scroll>
          </Col>
          <Col span="8">
            <Form class="step-form" ref="checkSuggestion" :model="suggestionData" :rules="ruleSuggestionData" :label-width="100">
              <FormItem label="审批意见" prop="remark">
                <Input v-model="suggestionData.remark" type="textarea" :rows="6" placeholder="请输入审批意见..."></Input>
              </FormItem>
              <FormItem label="操作">
                <Button type="primary" @click="handleCommit">发表意见</Button>
              </FormItem>
            </Form>
          </Col>
        </Row>
      </div>
    </div>
</template>

<script>
    import {GetSuggestionList, CreateSuggestion, DeleteSuggestion} from '@/api/sql/suggestion'

    export default {
      props: ['id', 'res'],
			watch:{
        res: function () {
          this.getData()
        }
      },
      data () {
        return {
          showHeader:false,
          page:1,
          count:1,
          results:[],
          columnsSuggestion: [
            {
              title: '时间',
              key: 'createtime',
              width: 150,
              render: (h, params) => {
                return h('div', {}, [params.row.createtime.split('.')[0].replace('T',' ')])
              }
            },
            {
              title: '用户',
              width: 150,
              key: 'username'
            },
            {
              title: '意见',
              key: 'remark'
            }
          ],
          suggestionData:{
            remark:''
          },
          ruleSuggestionData:{
            remark:[{ required: true, message: '请输入审批意见', trigger: 'blur' }],
          },

        }
      },
      methods: {

        refreshList (page) {
          this.$emit('refreshList', page)
          this.getData()
        },

        pageChange (page) {
          this.refreshList(page)
        },

        getData () {
          if (JSON.stringify(this.res) != '{}'){
            this.count = this.res.data.count
            this.results = this.res.data.results
          }
        },

        handleCommit () {
          this.$refs.checkSuggestion.validate((valid) => {
            if (!valid) {
              return
            }
            let data = this.suggestionData
            data.work_order = this.id
            CreateSuggestion(data)
              .then(response => {
                this.refreshList()
              })
          })

        }

      }

    }
</script>
