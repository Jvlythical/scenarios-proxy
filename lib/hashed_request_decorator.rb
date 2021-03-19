require 'digest/md5'

require_relative 'request_body_parser'

class HashedRequestDecorator

  def initialize(request)
    @request = request

    @ignored_headers = {}
    @ignored_query_params = {}
    @ignored_body_params = {}
  end
  
  ###
  #
  # @param ignored_components [Array<Hash>] e.g. [{"name":"script-name","type":1}]
  #
  def with_ignored_components(ignored_components)
    ignored_components.each do |ignored_component|
      component_name = ignored_component['name']

      case ignored_component['type']
      when COMPONENT_TYPES[:HEADER]
        @ignored_headers[component_name] = true
      when COMPONENT_TYPES[:QUERY_PARAM]
        @ignored_query_params[component_name] = true
      when COMPONENT_TYPES[:BODY_PARAM]
        @ignored_body_params[component_name] = true
      end
    end

    self
  end

  def query_params_hash
    params = []

    CGI.parse(@request.query_string).each do |key, value|
      next if @ignored_query_params[key]

      if value.is_a? Array
        value.each do |e|
          params << Digest::MD5.hexdigest(serialize_param(key, e))
        end
      else
        params << Digest::MD5.hexdigest(serialize_param(key, value))
      end
    end

    return '' if params.empty?

    Digest::MD5.hexdigest(params.sort.join('.'))
  end

  def body_params_hash
    values = []

    parser = RequestBodyParser.instance
    parser.parse(@request).each do |key, value|
      next if @ignored_body_params[key]

      values << Digest::MD5.hexdigest(serialize_param(key, value)) 
    end

    return '' if values.empty?

    Digest::MD5.hexdigest(values.sort.join('.'))
  end

  def body_text_hash
    text = @request.body.read
    return text if text.empty?
    Digest::MD5.hexdigest(text)
  end

  private 

  def serialize_param(key, val)
    "#{key}.#{val.to_s}"
  end
end
