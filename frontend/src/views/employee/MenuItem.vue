<template>
  <button class="btn btn-primary btn-employee" @click="$router.push({ name: 'Employee' })">
    <icon name="user" scale="2"/>
    <span class="btn-text">{{$tc('shared.employee', 1)}}</span>
  </button>
</template>
