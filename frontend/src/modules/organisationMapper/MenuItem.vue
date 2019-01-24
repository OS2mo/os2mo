<template>
  <button class="btn btn-success btn-mapper mt-3" @click="$router.push({ name: 'OrganisationMapper' })">
    <icon name="sitemap" scale="2"/>
    <span class="btn-text">{{$t('shared.organisation_mapping')}}</span>
  </button>
</template>
