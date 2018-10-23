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
      <div>
        <Row>
          <Col span="24">
            <Scroll height=220>
              <div class="wrapper">
                <div class="inner" v-for="(item, index) in handleResult" :value="item.value" :key="index">{{ item.value }} </div>
              </div>
            </Scroll>
          </Col>
        </Row>
      </div>
      <div>
        </br>
        <Button type="primary" size="large" @click="exportData"><Icon type="ios-cloud-download-outline"></Icon> 导出文件</Button>
        <span class="totalDesc">数据量共计 {{row.exe_affected_rows}} 条</span>
      </div>
    </div>
</template>

<script>
import axios from '../../../libs/http';

export default {
  props: ['row', 'handleResult'],
  created() {
    console.log(this.row)
  },
  methods: {
    exportData () {
      const sfx = '.data'
      let url = "/api/media/download/sqlhandle/" + this.row.id + sfx
      axios({
        method:'get',
        url:url,
        responseType:'blob',
      })
      .then((response) => {
        if (!response) {
            return
        }
        let url = window.URL.createObjectURL(response.data)
        let link = document.createElement('a')
        link.style.display = 'none'
        link.href = url
        link.setAttribute('download', this.row.id + sfx)
        document.body.appendChild(link)
        link.click()
      })
    },
    
  }

}
</script>


