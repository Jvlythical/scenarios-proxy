require 'singleton'
require 'yaml'

class RecordConfigFile
  include Singleton

  def initialize
    @config_file_path = File.join(File.dirname(__FILE__), '..', 'config', 'record.yml')
    @config = YAML.load_file(@config_file_path) 
    @environment = ENV['RAILS_ENV'] || 'development'
  end

  def mode
    @config.dig(@environment, 'mode') || ENV['MODE'] || MODE[:PROXY]
  end

  def scenarios_project_key
    @config.dig(@environment, 'scenarios_project_key') || ENV['SCENARIOS_PROJECT_KEY']
  end

  def scenarios_scenario_key
    @config.dig(@environment, 'scenarios_scenario_key') || ENV['SCENARIOS_SCENARIO_KEY']
  end

  def scenarios_api_key
    @config.dig(@environment, 'scenarios_api_key') || ENV['SCENARIOS_API_KEY']
  end

  def record_match_pattern
    @config.dig(@environment, 'record_match_pattern' || ENV['RECORD_MATCH_PATTERN'])
  end

  def record_policy
    @config.dig(@environment, 'record_policy' || ENV['RECORD_POLICY'])
  end

  def scenarios_url
    @config.dig(@environment, 'scenarios_url') || ENV['SCENARIOS_URL']
  end

  def service_url
    @config.dig(@environment, 'service_url') || ENV['SERVICE_URL']
  end

  def sync(scenarios_project_key, scenarios_scenario_key = nil)
    config = RecordConfig.find_by(
      scenarios_project_key: scenarios_project_key,
      scenarios_scenario_key: scenarios_scenario_key,
      environment: @environment,
    )
    return if config.nil?
    
    @config[@environment] = {} if @config[@environment].nil?
    
    config_hash = config.as_json
    ignored_columns = ['id', 'environment', 'created_at', 'updated_at']

    RecordConfig.column_names.each do |name|
      next if ignored_columns.include? name
      @config[@environment][name] = config_hash[name]
    end
  
    File.open(@config_file_path, 'w') do |fp|
      YAML.dump(@config, fp)
    end
  end

  def sync_to_database
    config = RecordConfig.find_by(
      scenarios_project_key: scenarios_project_key,
      scenarios_scenario_key: scenarios_scenario_key,
      environment: @environment,
    )

    if config.nil?
      config = RecordConfig.new(
        environment: @environment,
        scenarios_api_key: scenarios_api_key,
        scenarios_project_key: scenarios_project_key,
        scenarios_scenario_key: scenarios_scenario_key,
        scenarios_record_match_pattern: scenarios_record_match_pattern,
        scenarios_record_policy: upload_record_policy,
        scenarios_url: scenarios_url,
        service_url: service_url,
      )

      config.save
    else
      config.update(
        scenarios_api_key: scenarios_api_key,
        scenarios_url: scenarios_url,
        scenarios_record_match_pattern: scenarios_record_match_pattern,
        scenarios_record_policy: upload_record_policy,
        service_url: service_url,
      )
    end
  end
end
