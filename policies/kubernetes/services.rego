package main

# Denegar LoadBalancer en entornos locales
deny[msg] {
  input.kind == "Service"
  input.spec.type == "LoadBalancer"
  msg := "Services de tipo LoadBalancer no están permitidos. Usa ClusterIP o NodePort."
}
