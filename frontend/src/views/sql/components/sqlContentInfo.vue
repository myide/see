<style scoped>
    .inner {
        margin-bottom:10px
    }
</style>

<template>
    <div>
      <div>
        <Row>
          <Col span="24">
            <Scroll height=280>
              <div class="inner" v-for="(item, index) in sqlContent" :value="item.value" :key="index">{{ item.value }} </div>
            </Scroll>
          </Col>
        </Row>
      </div>
    </div>
</template>

<script>
export default {
  props: ['sqlContent'],
}
</script>
