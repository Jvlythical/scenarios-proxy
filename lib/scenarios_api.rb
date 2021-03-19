require 'net/http'

class ScenariosApi
  REQUESTS_ENDPOINT = '/requests'

  def initialize(service_url, api_key)
    @service_url = service_url
    @api_key = api_key 
  end

  def self.decode_project_key(jwt)
    token = JWT.decode(jwt, nil, false)
    payload = token[0]
    payload
  end

  def self.decode_scenario_key(jwt)
    token = JWT.decode(jwt, nil, false)
    payload = token[0]
    payload
  end

  def request_create(project_key, requests, **params)
    url = "#{@service_url}#{REQUESTS_ENDPOINT}" 
    uri = URI.parse(url)
    
    req = Net::HTTP::Post.new(uri)

    set_headers(req) 

    unless params[:scenario_key].nil? || params[:scenario_key].empty?
      scenario_id = decode_scenario_key(params[:scenario_key])['id']
      params[:scenario_id] = scenario_id
      params.delete :scenario_key
    end

    body = {
      project_id: decode_project_key(project_key)['id'],
      requests: requests,
    }.merge(params)

    req.set_form_data(body)

    send(uri, req)
  end

  def request_response(project_key, **query_params)
    url = "#{@service_url}#{REQUESTS_ENDPOINT}/response" 
    uri = URI.parse url

    unless query_params[:scenario_key].nil? || params[:scenario_key].empty?
      scenario_id = decode_scenario_key(query_params[:scenario_key])['id']
      query_params[:scenario_id] = scenario_id
      query_params.delete :scenario_key
    end
    
    params = {
      project_id: decode_project_key(project_key)['id']
    }.merge(query_params)

    uri.query = URI.encode_www_form(params)

    req = Net::HTTP::Get.new(uri)
    set_headers(req)
    
    Rails.logger.debug "  Request URL: #{uri}"

    send(uri, req) 
  end
  
  private

  def send(uri, req)
    Net::HTTP.start(uri.hostname, uri.port, use_ssl: uri.scheme == 'https') { |http|
      http.request(req)
    }
  end

  def set_headers(req)
    headers = default_headers
    headers.each do |name, value|
      req[name] = value
    end
  end

  def default_headers
    {
      X_API_KEY: @api_key
    }
  end
end
