#!/usr/bin/env ruby

require "net/http"
require "uri"

uri = ARGV[0]

print uri
while true do
  threads = []

  5.times do
    threads << Thread.new do
      Net::HTTP.get_response(URI.parse(uri))
      print "hitting #{uri}\n"
    end
  end

  threads.join

  sleep rand(2)
end

