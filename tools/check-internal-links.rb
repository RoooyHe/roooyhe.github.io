#!/usr/bin/env ruby
# frozen_string_literal: true

# Local internal-link checker that mirrors html-proofer's Internal/Images checks
# without needing libcurl (unavailable on this Windows box).
# Usage: ruby tools/check-internal-links.rb

require 'nokogiri'
require 'pathname'

site_dir = File.expand_path('_site', __dir__ + '/..')
failures = []
html_files = Dir.glob(File.join(site_dir, '**', '*.html'))

def resolve_target(base_file, target)
  base_dir = File.dirname(base_file)
  # strip anchor/fragment and query
  path = target.sub(/[#?].*\z/, '')
  return nil if path.empty?

  # decode %20 etc.
  decoded = URI.decode_www_form_component(path) rescue path
  File.expand_path(decoded, base_dir)
end

html_files.each do |file|
  doc = Nokogiri::HTML(File.read(file, encoding: 'UTF-8'))

  doc.css('img').each do |img|
    src = img['src']
    next if src.nil? || src.empty?
    next if src =~ %r{\A(?:https?:)?//} || src.start_with?('data:')

    target = resolve_target(file, src)
    next if target.nil?
    unless File.exist?(target)
      failures << "[Image] #{file} -> #{src} (resolved: #{target})"
    end
  end

  doc.css('a[href]').each do |a|
    href = a['href']
    next if href.nil? || href.empty?
    next if href =~ %r{\A(?:https?:)?//}
    next if href.start_with?('mailto:', 'tel:', 'javascript:', 'data:')
    next if href.start_with?('/') && !href.start_with?('//') # site-absolute: skip (baseurl-relative)

    target = resolve_target(file, href)
    next if target.nil?
    unless File.exist?(target)
      failures << "[Link] #{file} -> #{href} (resolved: #{target})"
    end
  end
end

if failures.empty?
  puts "OK: #{html_files.size} HTML files checked, no broken internal links/images."
  exit 0
else
  puts "FAILED: #{failures.size} broken internal link(s)/image(s):"
  failures.each { |f| puts "  #{f}" }
  exit 1
end
