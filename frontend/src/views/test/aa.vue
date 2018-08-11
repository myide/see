<style lang="less">
</style>

<template>
    <div>
        <Card>
            111222
            <Button @click="backPage"> 返回</Button>
            <Button @click="goHome"> home</Button>

        </Card>
    </div>
</template>

<script>
import {Button} from 'iview';
export default {
    components: {Button},
    methods: {
        backPage () {
            this.$router.go(-1);
        },
        goHome () {
            this.$router.push({
                name: 'check'
            });
        }
    }
};
</script>
