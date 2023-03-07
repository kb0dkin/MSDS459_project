CREATE MIGRATION m1yuetngveaqtxh5ndnf27y5dzvoubzf5zo7l3q6gxqmhucrhaes4a
    ONTO m1ljwtoyzk5knu6cu6nnjiuriaxlqvtmwancceapjstnocubyvueza
{
  ALTER TYPE default::Guitar {
      ALTER PROPERTY model {
          CREATE CONSTRAINT std::exclusive;
      };
  };
  ALTER TYPE default::Manufacturer {
      ALTER PROPERTY name {
          CREATE CONSTRAINT std::exclusive;
      };
  };
  ALTER TYPE default::Vendor {
      ALTER PROPERTY name {
          CREATE CONSTRAINT std::exclusive;
      };
  };
};
