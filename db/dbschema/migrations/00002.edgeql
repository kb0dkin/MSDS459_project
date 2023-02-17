CREATE MIGRATION m16c6fjljahhlxc3qenwdon3524reqwxflqtrgeemxtod3ff4tu4la
    ONTO m1paghr6vk32ump5knam2ndhivwkzoonegik6fvzbzfe7dxsubypdq
{
  ALTER TYPE default::Guitar {
      ALTER LINK seller {
          SET MULTI;
      };
  };
};
