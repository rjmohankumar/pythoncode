#!/usr/bin/env groovy

// Begin Pipeline
pipeline {
  agent {
    node {
      label 'deploy_linux_standard'
    }
  }
  environment{
    docker_container_name = "cname-alias-dns_testing:${env.BUILD_ID}"
  }
  parameters {
    text(name: 'SHORTNAME', description: 'enter ellucian shortname')
    text(name: 'HOSTED_ZONE', description: 'enter the hosted zone here')
  }
  stages {
    stage("stage for printing all DNS CNAMES"){
      steps{
        script{
          docker.build(docker_container_name)
        }
        script{
           withCredentials([string(credentialsId: 'site2site_db_site2siteuser_password_2', variable: 'S2S_DB_PASSWORD')
           ]){
                sh ('''
                    set +x
                    docker run -t --rm \\
                        $docker_container_name \\
                        --short-name "$SHORTNAME" \\
                        --dns-zone "$HOSTED_ZONE" \\
                        --db-password "$S2S_DB_PASSWORD" \\
                        --check-flag "yes"
                '''
            )
           }
        }
    }
    }

    stage("User Review") {
      steps{
        timeout(time: 1, unit: 'HOURS') {
        input 'Do you approve these changes?'
        }
      }
    }

    stage("stage for DNS modifications"){
      steps{
        script{
          docker.build(docker_container_name)
        }
        script{
           withCredentials([string(credentialsId: 'site2site_db_site2siteuser_password_2', variable: 'S2S_DB_PASSWORD')
           ]){
                sh ('''
                    set +x
                    docker run -t --rm \\
                        $docker_container_name \\
                        --short-name "$SHORTNAME" \\
                        --dns-zone "$HOSTED_ZONE" \\
                        --db-password "$S2S_DB_PASSWORD" \\
                        --check-flag "no"
                '''
            )
           }
        }
    }
    }
   }
}


