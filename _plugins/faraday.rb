require 'faraday'
require 'faraday/net_http'

Faraday.default_adapter = :net_http
Faraday.default_connection = Faraday.new do |builder|
  builder.use Faraday::Adapter::NetHttp
end