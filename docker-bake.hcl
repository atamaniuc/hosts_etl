// Group for parallel building of services
group "default" {
  targets = ["app-dev"]
}

// Base configuration for all app builds
target "app-base" {
  context    = "./app"
  dockerfile = "Dockerfile"
}

// Production build of the application
target "app" {
  inherits = ["app-base"]
  tags     = ["etl_app:latest"]
  args = {
    BUILD_ENV = "production"
  }
}

// Development build with additional tools
target "app-dev" {
  inherits = ["app-base"]
  tags     = ["etl_app:dev"]
  args = {
    BUILD_ENV = "development"
  }
}

// Testing build
target "app-test" {
  inherits = ["app-base"]
  tags     = ["etl_app:test"]
  args = {
    BUILD_ENV = "test"
  }
}
