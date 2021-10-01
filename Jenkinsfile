@Library("rd-apmm-groovy-ci-library@v1.x") _

pipeline {
    agent {
        label "ubuntu&&apmm-agent"
    }
    options {
        ansiColor('xterm') // Add support for coloured output
        buildDiscarder(logRotator(numToKeepStr: '10')) // Discard old builds
    }
    triggers {
        cron(env.BRANCH_NAME == 'master' ? 'H H(0-8) * * *' : '') // Build master some time every morning
    }
    parameters {
        string(name: "PYTHON_VERSION", defaultValue: "3.6", description: "Python version to make available in tox")
        booleanParam(name: "FORCE_ARTIFACTORYUPLOAD", defaultValue: false, description: "Force upload of python wheels to artifactory")
    }
    environment {
        http_proxy = "http://www-cache.rd.bbc.co.uk:8080"
        https_proxy = "http://www-cache.rd.bbc.co.uk:8080"
        PATH = "$HOME/.pyenv/bin:$PATH"
        WITH_DOCKER = "true"
        DOCKER_CONFIG = "$WORKSPACE/docker-config/"
    }
    stages {
        stage ("make lint") {
            steps {
                bbcMake 'lint'
            }
            post {
                always {
                    bbcGithubNotify(context: "lint", status: env.result)
                }
            }
        }
        stage ("make test") {
            steps {
                bbcMake 'test'
            }
            post {
                always {
                    bbcGithubNotify(context: "test", status: env.result)
                }
            }
        }
        stage ("make wheel") {
            steps {
                bbcMake 'wheel'
            }
            post {
                always {
                    bbcGithubNotify(context: "wheel", status: env.result)
                }
            }
        }
        stage ("make push") {
            when {
                anyOf {
                    expression { return params.FORCE_ARTIFACTORYUPLOAD }
                    expression { env.TAG_NAME != null }
                    expression {
                        bbcShouldUploadArtifacts(branches: ["master"])
                    }
                }
            }
            steps {
                withCredentials([usernamePassword(credentialsId: "171bbdf4-7ac0-4323-9d5c-a9fdc5317f45",
                        passwordVariable: 'TWINE_REPO_PASSWORD',
                        usernameVariable: 'TWINE_REPO_USERNAME')]) {
                    withEnv(["TWINE_REPO=https://artifactory-noforge.virt.ch.bbc.co.uk/artifactory/api/pypi/ap-python"]) {
                        bbcMake "push"
                    }
                }
            }
            post {
                always {
                    bbcGithubNotify(context: "push", status: env.result)
                }
            }
        }
    }
    post {
        always {
            bbcSlackNotify(channel: "#apmm-cloudfit")
        }
    }
}
