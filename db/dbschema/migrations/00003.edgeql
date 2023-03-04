CREATE MIGRATION m1mxovkjniut446vxbemcodhygasfli57umbundsavkm5gijnao4sq
    ONTO m16c6fjljahhlxc3qenwdon3524reqwxflqtrgeemxtod3ff4tu4la
{
  ALTER TYPE default::Guitar {
      CREATE PROPERTY country_of_origin -> std::str;
  };
  ALTER TYPE default::Guitar {
      CREATE PROPERTY cutaway -> std::str;
  };
  ALTER TYPE default::Guitar {
      CREATE PROPERTY description -> std::json;
  };
  ALTER TYPE default::Guitar {
      ALTER PROPERTY no_strings {
          RENAME TO num_frets;
      };
  };
  ALTER TYPE default::Guitar {
      CREATE PROPERTY num_strings -> std::int32;
  };
  CREATE SCALAR TYPE default::SourceType EXTENDING enum<Vendor, Independent>;
  CREATE TYPE default::ReviewSource {
      CREATE REQUIRED PROPERTY name -> std::str;
      CREATE PROPERTY sourceType -> default::SourceType;
  };
  ALTER TYPE default::Review {
      CREATE LINK source -> default::ReviewSource;
      CREATE PROPERTY best_for -> std::json;
      CREATE PROPERTY cons -> std::json;
      CREATE PROPERTY date -> std::datetime;
      CREATE PROPERTY pros -> std::json;
  };
  CREATE TYPE default::Reviewer {
      CREATE MULTI LINK source -> default::ReviewSource;
      CREATE MULTI LINK review -> default::Review;
      CREATE REQUIRED PROPERTY name -> std::str;
  };
};
