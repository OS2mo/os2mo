<template>
    <button type="button" class="btn btn-primary btn-workflow">
      <icon class="btn-icon" :name="icon"/>
      <label class="btn-label">{{label}}</label>
    </button>
</template>

<script>
  export default {
    name: 'MoWorkflowButton',
    props: {
      label: {
        default: 'New Workflow',
        type: String
      },
      icon: {
        default: 'plus-circle',
        type: String
      }
    }
  }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  .btn-workflow {
    display: block;
    height: 38px;
    margin-bottom: 4px;
    text-align: left;
    width: 300px;
    position: relative;
    right: 0;
    transition: right .15s;
    transition-delay: .05s;
    transition-timing-function: ease-in;

    &:hover {
      right: 235px;
      transition: right .25s;
      transition-timing-function: ease-out;
    }

    .btn-label {
      padding-left: 25px;
      position: absolute;
    }

    .btn-icon {
      width: 24px;
      height: 24px;
    }
  }
</style>