package main

# Denegar si usa imagen con tag "latest"
deny[msg] {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  endswith(container.image, ":latest")
  msg := sprintf("Imagen '%v' usa tag 'latest'. Usa un tag específico como sha-abc123.", [container.image])
}

# Denegar si no tiene resource limits
deny[msg] {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  not container.resources.limits
  msg := sprintf("Contenedor '%v' no tiene resource limits definidos.", [container.name])
}

# Denegar si corre como root
deny[msg] {
  input.kind == "Deployment"
  not input.spec.template.spec.securityContext.runAsNonRoot
  msg := "El pod debe tener runAsNonRoot: true en el securityContext."
}
