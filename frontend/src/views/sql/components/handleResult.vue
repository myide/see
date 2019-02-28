<style scoped>
  .wrapper {
      background-color:black;
      color:white 
  }
  .inner {
      margin-bottom: 10px;
      margin-left: 10px
  }
  .totalDesc {
      margin-left: 10px;
      color: #7b7b7b
  }
</style>

<template>
    <div>
      <div v-if="row.type=='select'">
        <Row>
          <Col span="24">
            <Scroll height=220>       
              <div class="wrapper">
                <div class="inner" v-for="(item, index) in handleResultExecute" :value="item.value" :key="index">{{ item.value.replace(/^\"|\"$/g,'') }}</div>
              </div>
            </Scroll>
          </Col>
        </Row>   
      </div>

      <div v-else>
        <Tabs @on-click="changeTab">
          <TabPane label="Inception审核" name="handle_result_check">
            <Row>
              <Col span="24">
                <Scroll height=220>       
                  <div class="wrapper">
                    <div class="inner" v-for="(item, index) in handleResultCheck" :value="item.value" :key="index">{{ item.value }}</div>
                  </div>
                </Scroll>
              </Col>
            </Row>
          </TabPane>
          
          <TabPane label="Inception执行" name="handle_result_execute">
            <Row>
              <Col span="24">
                <Scroll height=220>       
                  <div class="wrapper">
                    <div class="inner" v-for="(item, index) in handleResultExecute" :value="item.value" :key="index">{{ item.value }}</div>
                  </div>
                </Scroll>
              </Col>
            </Row>          
          </TabPane>

          <TabPane label="Inception回滚" name="handle_result_rollback">
            <Row>
              <Col span="24">
                <Scroll height=220>       
                  <div class="wrapper">
                    <div class="inner" v-for="(item, index) in handleResultRollback" :value="item.value" :key="index">{{ item.value }}</div>
                  </div>
                </Scroll>
              </Col>
            </Row> 
          </TabPane>
            
        </Tabs>

      </div>
      <div>
        </br>
        <Button type="primary" size="large" @click="exportData"><Icon type="ios-cloud-download-outline"></Icon> 导出文件</Button>
        <span class="totalDesc">数据量共计 {{dataLength}} 条</span>
      </div>
    </div>
</template>

<script>
import axios from '../../../libs/http';

export default {

  props: ['row', 'handleResultCheck', 'handleResultExecute', 'handleResultRollback'],
  
  created() {
    this.tabName = this.row.type == 'select' ? 'handle_result_execute' : 'handle_result_check'
    this.dataLength = this.row.type == 'select' ? this.handleResultExecute.length : this.handleResultCheck.length
  },

  data () {
    return {
      tabName:'',
      dataLength:0,
      handleMap:{
        handle_result_check:this.handleResultCheck ? this.handleResultCheck : [],
        handle_result_execute:this.handleResultExecute ? this.handleResultExecute : [],
        handle_result_rollback:this.handleResultRollback ? this.handleResultRollback : []
      },
    }
  },

  methods: {

    changeTab (data) {
      this.tabName = data
      this.dataLength = this.handleMap[data].length
    },

    exportData () {
      const sfx = '.data'
      let url = "/api/media/download/sqlhandle/" + this.row.id + sfx
      const params = {data_type: this.tabName}
      axios({
        method:'get',
        url:url,
        responseType:'blob',
        params
      })
      .then((response) => {
        if (!response) {
          return
        }
        let url = window.URL.createObjectURL(response.data)
        let link = document.createElement('a')
        link.style.display = 'none'
        link.href = url
        link.setAttribute('download', this.tabName + '_' + this.row.id + sfx)
        document.body.appendChild(link)
        link.click()
      })
    },
    
  }

}
</script>
