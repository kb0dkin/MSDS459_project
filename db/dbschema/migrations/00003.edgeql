CREATE MIGRATION m13ijpmbphsljn6uttsag64gqf4cvqd3thntxydyfk226pp6j53y6a
    ONTO m1yuetngveaqtxh5ndnf27y5dzvoubzf5zo7l3q6gxqmhucrhaes4a
{
  ALTER TYPE default::ReviewSource {
      ALTER PROPERTY name {
          CREATE CONSTRAINT std::exclusive;
      };
  };
  ALTER TYPE default::Reviewer {
      ALTER PROPERTY name {
          CREATE CONSTRAINT std::exclusive;
      };
  };
};
