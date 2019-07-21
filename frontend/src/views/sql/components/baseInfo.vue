<style scoped>
</style>

<template>
    <div>
      <div style="margin-top:10px;margin-bottom:10px">
        <Row>
          <Col span="2">
            <p> <b>ID：</b> </p>
          </Col>
          <Col span="10">
            <p> {{row.id}} </p>
          </Col>
          <Col span="2">
            <p> <b>目标库：</b>  </p>
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
            <p> {{getTime}} </p>
          </Col>
          <Col span="2">
            <p> <b>影响的行数：</b>  </p>
          </Col>
          <Col span="10">
            <p> {{row.affected_rows}} </p>
          </Col>
        </Row>

        <Row>
          <Col span="2">
            <p> <b>发起人：</b> </p>
          </Col>
          <Col span="10">
            <p> {{row.commiter}} </p>
          </Col>
          <Col span="2">
            <p> <b>核准人：</b>  </p>
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
            <Tag v-if="row.env == 'prd'" type="border" color="orange">生产</Tag>
            <Tag v-if="row.env == 'test'" type="border" color="gray">测试</Tag>
          </Col>
          <Col span="2">
            <p> <b>工单状态：</b>  </p>
          </Col>
          <Col span="10">
            <p v-if="row.status == -3" > <Tag>回滚成功</Tag> </p>
            <p v-else-if="row.status == -2" > <Tag>已暂停</Tag> </p>
            <p v-else-if="row.status == -1" > 
              <Tag v-if="row.is_manual_review == false"  color="blue">待执行</Tag>
              <Tag v-else color="blue">待审批</Tag>
            </p>
            <p v-else-if="row.status == 0" > <Tag color="green">执行成功</Tag> </p>
            <p v-else-if="row.status == 1" > <Tag color="yellow">已放弃</Tag> </p>
            <p v-else-if="row.status == 2" > <Tag color="red">任务异常</Tag> </p>
            <p v-else-if="row.status == 3" > <Tag color="blue">审批通过</Tag> </p>
            <p v-else-if="row.status == 4" > <Tag color="yellow">审批驳回</Tag> </p>
            <p v-else-if="row.status == 5" > <Tag color="blue">已定时</Tag> </p>
            <p v-else-if="row.status == 6" > <Tag color="yellow">执行中</Tag> </p>
            <p v-else-if="row.status == 7" > <Tag color="yellow">回滚中</Tag> </p>
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
    </div>
</template>

<script>
export default {
  props: ['row', 'sqlContent'],
  computed: {
    getTime: function () {
      return this.row.createtime.split('.')[0].replace('T',' ')
    } 
  }
}
</script>


