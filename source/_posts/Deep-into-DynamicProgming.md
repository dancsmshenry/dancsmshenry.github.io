---
title: Deep into DynamicProgming
top: false
cover: false
toc: true
mathjax: true
date: 2022-10-10 12:35:33
password:
summary:
tags:
- Algorithm
- DynamicProgming
categories:
---



# 路径问题（Path Problem）

## 62、不同路径

二维数组记录状态，通过滚动数组优化可以变为一维数组

```cpp
class Solution {
public:
    int uniquePaths(int m, int n) {
        vector<int> dp(n, 1);

        for (int i = 1; i < m; ++ i) {
            for (int j = 1; j < n; ++ j) {
                dp[j] += dp[j - 1];
            }
        }

        return dp.back();
    }
};
```

<br/>

## 63、不同路径II

路上有障碍物，需要避开障碍物统计路线数量

```cpp
class Solution {
public:
    int uniquePathsWithObstacles(vector<vector<int>>& obstacleGrid) {
        int n = obstacleGrid.size(), m = obstacleGrid[0].size();
        vector<int> dp(m + 1, 0);
        dp[0] = 1; //	最左边的竖线的一条路，只能一直往下走，所以为1
        if (obstacleGrid[0][0] == 1) {
            return 0;
        }

        for (int i = 0; i < n; ++ i) {
            for (int j = 0; j < m; ++ j) {
                if (obstacleGrid[i][j] == 1) {
                    dp[j] = 0;
                } else if (j > 0 && obstacleGrid[i][j] == 0) {
                    dp[j] += dp[j - 1];
                }
            }
        }

        return dp.back();
    }
};
```

<br/>

## 64、最小路径和

统计到达目标点的最小路径和；也是二维数组，滚动优化后变为一维数组

```cpp
class Solution {
public:
    int minPathSum(vector<vector<int>>& grid) {
        int n = grid.size(), m = grid[0].size();
        vector<int> dp(m, grid[0][0]);

        for (int i = 1; i < m; ++ i) {
            dp[i] = dp[i - 1] + grid[0][i];
        }

        for (int i = 1; i < n; ++ i) {
            dp[0] += grid[i][0];
            for (int j = 1; j < m; ++ j) {
                dp[j] = min(dp[j - 1], dp[j]) + grid[i][j];
            }
        }

        return dp.back();
    }
};

//	另一种优化为一维数组的方法
class Solution {
public:
    int minPathSum(vector<vector<int>>& grid) {
        int n = grid.size(), m = grid[0].size();
        vector<int> dp(m + 1, INT_MAX);
        dp[0] = 0;

        for (int i = 1; i <= n; ++ i) {
            for (int j = 1; j <= m; ++ j) {
                dp[j] = min(dp[j - 1], dp[j]) + grid[i - 1][j - 1];
            }
            dp[0] = INT_MAX;
        }

        return dp.back();
    }
};
```

<br/>

## 120、最小三角路径和

杨辉三角；滚动数组优化

```cpp
class Solution {
public:
    int minimumTotal(vector<vector<int>>& triangle) {
        int n = triangle.size();
        vector<int> dp(n, 0);

        for (int i = 0; i < n; ++ i) {
            for (int j = i; j >= 0; -- j) {
                if (j == 0) {
                    dp[j] += triangle[i][j];
                } else if (j == i) {
                    dp[j] = dp[j - 1] + triangle[i][j];
                } else {
                    dp[j] = min(dp[j], dp[j - 1]) + triangle[i][j];
                }
            }
        }

        return *min_element(dp.begin(), dp.end());
    }
};
```

<br/>

## 221、最大正方形

用滚动数组优化（注意滚动数组要重置状态）

```cpp
class Solution {
public:
    int maximalSquare(vector<vector<char>>& matrix) {
        int n = matrix.size(), m = matrix[0].size();
        vector<vector<int>> dp(n + 1, vector<int>(m + 1, 0));
        int res = 0;

        for (int i = 1; i <= n; ++ i ) {
            for (int j = 1; j <= m; ++ j) {
                if (matrix[i - 1][j - 1] == '1') {
                    dp[i][j] = min(dp[i][j - 1], min(dp[i - 1][j], dp[i - 1][j - 1])) + 1;
                    res = max(res, dp[i][j]);
                }
            }
        }

        return res * res;
    }
};

//滚动数组优化
class Solution {
public:
    int maximalSquare(vector<vector<char>>& matrix) {
        int n = matrix.size(), m = matrix[0].size();
        vector<vector<int>> dp(2, vector<int>(m + 1, 0));
        int res = 0;

        for (int i = 1; i <= n; ++ i ) {
            int second = i % 2, first = 1 - second;
            for (int j = 1; j <= m; ++ j) {
                dp[second][j] = 0;
                if (matrix[i - 1][j - 1] == '1') {
                    dp[second][j] = min(dp[second][j - 1], min(dp[first][j], dp[first][j - 1])) + 1;
                    res = max(res, dp[second][j]);
                }
            }
        }

        return res * res;
    }
};
```

<br/>

## 416、分割等和子集

给你一个 只包含正整数 的 非空 数组 nums 。请你判断是否可以将这个数组分割成两个子集，使得两个子集的元素和相等

这套题和最小三角路径和几乎是一模一样的dp思路，但是难就难在，很难将问题转换为路径问题...（而且由此也推出了滚动数组优化的两种情况）

```cpp
class Solution {
public:
    bool canPartition(vector<int>& nums) {
        int sum = accumulate(nums.begin(), nums.end(), 0), n = nums.size();
        if (sum % 2 == 1){
            return false;
        }
        sum = sum / 2;
    
        vector<vector<int>> f(n + 1, vector<int> (sum + 1, false));
        for (int i = 1; i <= n; ++ i) {
            if (nums[i - 1] > sum) {
                return false;
            }
            f[i][nums[i - 1]] = true;  
            for (int j = 1; j <= sum; ++ j) {
                f[i][j] |= f[i - 1][j];
                if (j + nums[i - 1] <= sum) {
                    f[i][j + nums[i - 1]] |= f[i - 1][j];
                }
            }
            if (f[i][sum]) {
                return true;
            }
        }

        return false;
    }
};

// 滚动数组优化
class Solution {
public:
    bool canPartition(vector<int>& nums) {
        int sum = accumulate(nums.begin(), nums.end(), 0), n = nums.size();
        if (sum % 2 == 1){
            return false;
        }
        sum = sum / 2;
    
        vector<int> f(sum + 1, false);
        f[0] = true;
        for (int i = 1; i <= n; ++ i) {
            if (nums[i - 1] > sum) {
                return false;
            }
            for (int j = sum; j >= 0; -- j) {
                if (j + nums[i - 1] <= sum) {
                    f[j + nums[i - 1]] |= f[j];
                }
            }
            if (f[sum]) {
                return true;
            }
        }

        return false;
    }
};
```

<br/>

<br/>

<br/>

# Coins Problem

## 零钱兑换

- jd：最少需要多少硬币凑出amount

- 这里很关键的一步就是dp数组的初始化流程，将每个属性都设为INT_MAX

- 本质上就是**完全背包问题**

- ```cpp
  class Solution {
  public:
      int coinChange(vector<int>& coins, int amount) {
          vector<int> dp(amount + 1, INT_MAX);
          dp[0] = 0;
  
          for (int i = 1; i <= amount; ++ i) {
              for (auto& coin: coins) {
                  if (i >= coin && dp[i - coin] != INT_MAX) {
                      dp[i] = min(dp[i], dp[i - coin] + 1);
                  }
              }
          }
  
          return dp[amount] == INT_MAX ? -1: dp[amount];
      }
  };
  ```



## 零钱兑换II

- jd：凑出amount有多少种方法

- 这里的坑点：循环的顺序和I是反过来的，需要注意（假设这里的数量5是由1112凑成的，就会只有这一种方法，但是如果改变循环顺序，即变为对于每个i，遍历所有的硬币，这样就会造成重复了）

- PS：

  - 对于零钱兑换I来说，问的是硬币数量，要取得amount总值的硬币，就要假设枚举最后一次拿的是哪一种硬币，然后从中选出数量最少的
  - 对于零钱兑换II来说，问的是有多少种方法，如果继续沿用上面的方法，就会出现问题
  - 比如说硬币4和硬币5组成了amount值9，那么要得到9，枚举这两枚硬币的话，就会出现两种方法，而实际上都是同一种的
  - 所以要改变循环思路，即改变最后子问题的问法（即此时的子问题不是当前解）
  - 正确的子问题应该是在已经组成amount的方法中，出现了新的一种类型的硬币的时候，再用这种新的硬币组成amount，会有多少种方法
  - 所以要逐枚逐枚的将硬币放入组成amount的方法中

- 简答：求方法数的话，思路应该是，在只拿当前那么多的硬币的情况下，有多少种方法，然后再逐枚逐枚往后推

- ```cpp
  class Solution {
  public:
      int change(int amount, vector<int>& coins) {
          vector<int> dp(amount + 1, 0);
          dp[0] = 1;
  
          for (auto& coin: coins) {
              for (int i = coin; i <= amount; ++ i) {
                  dp[i] += dp[i - coin];
              }
          }
  
          return dp[amount];
      }
  };
  ```





# Stock Problem

## 买卖股票的最佳时机I

- jd：只能买卖一次股票（同 剑指 Offer 63. 股票的最大利润）

- 只要找到前面最低点，和这个点以后的最高点的差值即可

- ```cpp
  class Solution {
  public:
      int maxProfit(vector<int>& prices) {
          int minn = INT_MAX;
          int res = 0;
  
          for (auto& price: prices) {
              minn = min(minn, price);
              res = max(res, price - minn);
          }
  
          return res;
      }
  };
  ```



## 买卖股票的最佳时机II

- jd：能无限次的买卖股票

- 只要当前的价格大于昨天的，就卖股票拿钱

- ```cpp
  class Solution {
  public:
      int maxProfit(vector<int>& prices) {
          int res = 0;
          int n = prices.size();
  
          for (int i = 1; i < n; ++ i) {
              if (prices[i] > prices[i - 1]) {
                  res += (prices[i] - prices[i - 1]);
              }
          }
  
          return res;
      }
  };
  ```



## 买卖股票的最佳时机III

- jd：最多能买卖两次股票

- 每天可以分为两种状态：

  - 没股票 = max（昨天没股票，昨天有股票今天卖股票）
  - 有股票 = max（昨天有股票，昨天没股票今天买股票）

- 再结合最多能买卖两次股票，就变为：

  - 没股票 = max（昨天没股票（处于同一笔交易中），昨天有股票今天卖股票（处于同一笔交易））
  - 有股票 = max（昨天有股票（处于同一笔交易中），昨天没股票今天买股票（进入新一笔交易中））

- 所以这里就把分为两个数组sell和hold，第一个下标表示当前的天数是多少，第二个表示当前是第几个交易阶段

- ```cpp
  class Solution {
  public:
      int maxProfit(vector<int>& prices) {
          int n = prices.size();
          /*表示当前持有股票，这里必须要设置为INT_MIN，因为对于i=1的时候，此时对应的是prices中的0，那么要持有股票的话，就只能当前买股票，不能用前一天的数据
          而当天买股票会导致值为负数，为了防止这一点，就设为INT_MIN，使得当天要股票的话，就必须当天买，不能推到昨天*/
          vector<vector<int>> hold(n + 1, vector<int> (3, INT_MIN));
          /*当前没股票*/
          vector<vector<int>> sell(n + 1, vector<int> (3, 0));
  
          for (int i = 1; i <= n; ++ i) {
              for (int j = 1; j < 3; ++ j) {
                  /*第i天有股票，要么是第i-1天没有股票，第i天买的；要么是第i-1天有股票*/
                  hold[i][j] = max(hold[i - 1][j], sell[i - 1][j - 1] - prices[i - 1]);
                  /*第i天没有股票，要么是第i-1天有股票，然后第i天卖出的；要么是第i-1天就没有股票*/
                  sell[i][j] = max(sell[i - 1][j], hold[i - 1][j] + prices[i - 1]);
              }
          }
  
          return sell[n][2];
      }
  };
  
  //滚动数组优化
  class Solution {
  public:
      int maxProfit(vector<int>& prices) {
          int n = prices.size();
          int sell1 = 0;
          int sell2 = 0;
          int hold1 = -prices[0];
          int hold2 = -prices[0];
  
          for (int i = 0; i < n; ++ i) {
              sell1 = max(sell1, hold1 + prices[i]);
              hold1 = max(hold1, -prices[i]);
              sell2 = max(sell2, hold2 + prices[i]);
              hold2 = max(hold2, sell1 - prices[i]); 
          }
  
          return sell2;
      }
  };
  ```

- 这里有个很坑的地方，就有点难以理解：

  - 其实当j等于2的时候，真的不代表它经过了两次交易，有可能是前一段中价格实在太低了，就没有买股票，所以值就是0（这里数组初始化的时候就有了），当出现合适的时候就买了股票，记录为第二笔交易
  - 而我们这里对于每一天，都记载了当前是第一笔交易或是第二笔交易的情况，所以算得上是考虑周全了

- 这里我对dp的一个感悟就是，将问题变为一个一个子问题，然后从最后一步看是否符合dp模型，即最优解是否符合状态转移这个过程



## 买卖股票的最佳时机IV

- jd：最多能买卖k次股票

- 和上面的情况一模一样了属于是.....

- ```cpp
  class Solution {
  public:
      int maxProfit(int k, vector<int>& prices) {
          int n = prices.size();
          /*表示当前持有股票，这里必须要设置为INT_MIN，因为对于i=1的时候，此时对应的是prices中的0，那么要持有股票的话，就只能当前买股票，不能用前一天的数据
          而当天买股票会导致值为负数，为了防止这一点，就设为INT_MIN，使得当天要股票的话，就必须当天买，不能推到昨天*/
          vector<vector<int>> hold(n + 1, vector<int> (k + 1, INT_MIN));
          /*当前没有股票*/
          vector<vector<int>> sell(n + 1, vector<int> (k + 1, 0));
  
          for (int i = 1; i <= n; ++ i) {
              for (int j = 1; j < k + 1; ++ j) {
                  /*第i天有股票，要么是第i-1天没有股票，第i天买的；要么是第i-1天有股票*/
                  hold[i][j] = max(hold[i - 1][j], sell[i - 1][j - 1] - prices[i - 1]);
                  /*第i天没有股票，要么是第i-1天有股票，然后第i天卖出的；要么是第i-1天就没有股票*/
                  sell[i][j] = max(sell[i - 1][j], hold[i - 1][j] + prices[i - 1]);
              }
          }
  
          return sell[n][k];
      }
  };
  
  //滚动数组优化
  class Solution {
  public:
      int maxProfit(int k, vector<int>& prices) {
          int n = prices.size();
          vector<int> hold(k + 1, INT_MIN);
          vector<int> sell(k + 1, 0);
  
          for (int i = 0; i < n; ++ i) {
              for (int j = 1; j < k + 1; ++ j) {
                  int mid = hold[j];
                  hold[j] = max(hold[j], sell[j - 1] - prices[i]);
                  sell[j] = max(sell[j], mid + prices[i]);
              }
          }
  
          return sell[k];
      }
  };
  ```



## 最佳买卖股票时机含冷冻期

- jd：能无限买卖股票，但是卖出股票的第二天是不能买入股票的（即冷冻期为1天）

- 参考股票模型，然后魔改一下，注意init即可

- 拓展：如果冷冻期是2天，3天，那也是一样的

- PS：

  - 股票问题最难优化的部分其实是，要找到方程到底是依赖于那几个变量，其次是如何调整更新各个变量的顺序
  - 比如说本题，每次更新都只需要当前位置的前两个位置的sell，当前位置的前一个hold
  - 所以就可以确认只需要sell1，sell2和hold三个变量，接着就是要确认更新顺序了
  - 发现当前的hold需要的是前一个hold和sell1；当前的sell2需要的是前一个hold和前一个sell2；当前的sell1需要的是前一个sell2
  - 即可知，需要一个中间变量来存放前一个sell2，然后再更新sell2（不能先更新hold，因为这里需要前一个hold），再就是更新hold，最后用中间变量更新sell1

- ```cpp
  class Solution {
  public:
      int maxProfit(vector<int>& prices) {
          int n = prices.size();
          /*判断边界情况*/
          if (n < 2) {
              return 0;
          }
          /*init数组*/
          vector<int> sell(n, 0);
          vector<int> hold(n, 0);
          /*最开始持有的话，就是第一天股票的价格，不过这里可以不用初始化，因为后面的遍历时不看这个的.....*/
          hold[0] = -prices[0];
          /*第二天买的话就看谁的价格更低一点*/
          hold[1] = max(-prices[1], -prices[0]);
          /*第二天卖的话，看有无利润喽*/
          sell[1] = max(0, prices[1] - prices[0]);
  
          for (int i = 2; i < n; ++ i) {
              sell[i] = max(sell[i - 1], hold[i - 1] + prices[i]);
              /*如果今天有股票的话，要么昨天有，要个过了冷冻期再才能买股票*/
              hold[i] = max(hold[i - 1], sell[i - 2] - prices[i]);
          }
  
          return sell[n - 1];
      }
  };
  
  //滚动数组优化
  class Solution {
  public:
      int maxProfit(vector<int>& prices) {
          int n = prices.size();
          if (n < 2) {
              return 0;
          }
          int sell1 = 0;
          int sell2 = max(0, prices[1] - prices[0]);
          int hold = max(-prices[1], -prices[0]);
  
          for (int i = 2; i < n; ++ i) {
              int mid = sell2;
              sell2 = max(sell2, hold + prices[i]);
              hold = max(hold, sell1 - prices[i]);
              sell1 = mid;
          }
  
          return sell2;
      }
  };
  ```



## 买卖股票的最佳时机含手续费

- jd：可以无限买卖股票，但买卖股票有手续费

- 太经典的模型了.....

- ```cpp
  class Solution {
  public:
      int maxProfit(vector<int>& prices, int fee) {
          int n = prices.size();
          if (n < 2) {
              return 0;
          }
          vector<int> sell(n, 0);
          vector<int> hold(n, -prices[0]);
  
          for(int i = 1; i < n; ++ i) {
              sell[i] = max(sell[i - 1], hold[i - 1] + prices[i] - fee);
              hold[i] = max(hold[i - 1], sell[i - 1] - prices[i]);
          }
  
          return sell[n - 1];
      }
  };
  
  //发现sell和hold只依赖前面一个，所以可以滚动数组优化
  class Solution {
  public:
      int maxProfit(vector<int>& prices, int fee) {
          int n = prices.size();
          if (n < 2) {
              return 0;
          }
          int sell = 0;
          int hold = -prices[0];
  
          for(int i = 1; i < n; ++ i) {
              sell = max(sell, hold + prices[i] - fee);
              hold = max(hold, sell - prices[i]);
          }
  
          return sell;
      }
  };
  ```



## 乘积最大子数组

- PS：我觉得这道题和股票问题很像，是因为这两类题的状态都是由前一个状态和另一个状态推导过来的

- ```cpp
  class Solution {
  public:
      int maxProduct(vector<int>& nums) {
          int n = nums.size();
          int res = nums[0];
          vector<int> fmax(n + 1, nums[0]);
          vector<int> fmin(n + 1, nums[0]);
  
          for (int i = 1; i < n; ++ i) {
              fmax[i] = max(nums[i], max(nums[i] * fmax[i - 1], nums[i] * fmin[i - 1]));
              fmin[i] = min(nums[i], min(nums[i] * fmax[i - 1], nums[i] * fmin[i - 1]));
              res = max(fmax[i], res);
          }
  
          return res;
      }
  };
  ```



## 环状最大两段子段和

- 吉比特笔试，洛谷P1121

- ```cpp
  #include <iostream>
  #include <vector>
  
  using namespace std;
  
  class Solution {
  public:
      int maxProfit(int k, vector<int>& prices) {
          int n = prices.size();
          vector<int> hold(k + 1, INT_MIN);
          vector<int> sell(k + 1, 0);
  
          for (int i = 0; i < n; ++ i) {
              for (int j = 1; j < k + 1; ++ j) {
                  int mid = hold[j];
                  hold[j] = max(hold[j], sell[j - 1] - prices[i]);
                  sell[j] = max(sell[j], mid + prices[i]);
              }
          }
  
          return sell[k];
      }
  
      int solve(vector<int>& arrs) {
          int n = arrs.size();
          vector<int> counts(n + 1, 0);
          for (int i = 1; i <= n; ++ i) {
              counts[i] = counts[i - 1] + arrs[i - 1];
          }
  
          return maxProfit(3, counts);
      }
  };
  
  int main() {
      vector<int> arrs{1,-1,1,-1,1};
      Solution s1;
      cout << s1.solve(arrs) << endl;
      return 0;
  }
  ```



# Knapsack Problem

## 01背包问题

- jd：

  - 有`N`件物品和一个容量是`V`的背包。每件物品**只能使用一次**（所以是01背包），第`i`件物品的体积是`vi`，价值是`wi`
  - 求解将哪些物品装入背包，可使这些物品的总体积不超过背包容量，且总价值最大
  - 输出最大价值

- 因为只能拿一次，所以在一维数组的时候**必须要倒序**

- ```cpp
  class Solution {
  public:
      int zero_one_back_problem(vector<int>& weight, vector<int>& value, int capacity) {
  		int n = weight.size();
          vector<vector<int>> dp(n + 1, vector<int>(capacity + 1, 0));
          
          for (int i = 1; i <= n; ++ i) {
              for (int j = 1; j <= capacity; ++ j) {
                  if (j < weight[i - 1]) {
                      dp[i][j] = dp[i - 1][j];
                  } else {
                      dp[i][j] = max(dp[i - 1][j], dp[i - 1][j - weight[i - 1]] + value[i - 1]);
                  }
              }
          }
          
          return dp[n][capacity];
      }
  };
  
  //滚动数组优化
  class Solution {
  public:
      int zero_one_back_problem(vector<int>& weight, vector<int>& value, int capacity) {
  		int n = weight.size();
          vector<vector<int>> dp(capacity + 1, 0);
          
          for (int i = 1; i <= n; ++ i) {
              for (int j = capacity; j >= weight[i - 1]; -- j) {
                  dp[j] = max(dp[j], dp[j - weight[i - 1]] + value[i - 1]);
              }
          }
          
          return dp[capacity];
      }
  };
  ```



## 完全背包问题

- jd：

  - 有`N`种物品和一个容量是`V`的背包，每种物品**都有无限件可用**（所以是完全背包问题），第`i`种物品的体积是`vi`，价值是 wi
  - 求解将哪些物品装入背包，可使这些物品的总体积不超过背包容量，且总价值最大
  - 输出最大价值

- 因为是无限次数的，所以不需要倒序

- ```cpp
  class Solution {
  public:
      int intirely_back_problem(vector<int>& weight, vector<int>& value, int capacity) {
          int n = weight.size();
          vector<vector<int>> dp(n + 1, vector<int>(capacity + 1, 0));
          
          for (int i = 1; i <= n; ++ i) {
              for (int j = 1; j <= capacity; ++ j) {
                  dp[i][j] = dp[i - 1][j];
                  if (j >= weight[i - 1]) {
                      dp[i][j] = max(dp[i][j - weight[i - 1]] + value[i - 1], dp[i][j]);
                  }
              }
          }
          
          return dp[n][capacity];
      }
  };
  
  //滚动数组优化
  class Solution {
  public:
      int intirely_back_problem(vector<int>& weight, vector<int>& value, int capacity) {
          int n = weight.size();
          vector<int> dp(capacity + 1, 0);
          
          for (int i = 1; i <= n; ++ i) {
              for (int j = 1; j <= capacity; ++ j) {
                  if (j >= weight[i - 1]) {
                      dp[j] = max(dp[j], dp[j - weight[i - 1]] + value[i - 1]);
                  }
              }
          }
          
          return dp[capacity];
      }
  };
  ```





# House Robber

## 打家劫舍I

- jd：相邻的房屋被偷会自动报警

- ```cpp
  class Solution {
  public:
      int rob(vector<int>& nums) {
          int n = nums.size();
          if (n == 1) {
              return nums[0];
          }
          vector<int> dp(n, 0);
          dp[0] = nums[0];
          dp[1] = max(nums[0], nums[1]);
  
          for (int i = 2; i < n; ++ i) {
              dp[i] = max(dp[i - 1], dp[i - 2] + nums[i]);
          }
  
          return dp[n - 1];
      }
  };
  
  //滚动数组优化
  class Solution {
  public:
      int rob(vector<int>& nums) {
          int n = nums.size();
          if (n == 1) {
              return nums[0];
          }
  
          vector<int> dp{nums[0], max(nums[0], nums[1])};
  
          for (int i = 2; i < n; ++ i) {
              dp[i % 2] = max(dp[1 - i % 2], dp[i % 2] + nums[i]);
          }
  
          return dp[1 - n % 2];
      }
  };
  ```



## 打家劫舍II

- jd：房子是环绕一圈的，其他条件同I

- 复盘一下使用二进制滚动数组时的一个错误(这里其实最好不要用二进制，因为，我们不知道begin是奇数还是偶数，这会导致我们后面遍历i%2的时候不好处理，比如说begin如果是奇数，那begin一开始就要放到1的位置；如果begin是偶数的话，那begin一开始就要放到0的位置，这样在最后求解的时候就会很麻烦，因为不知道到底应该取dp[0]还是取dp[1])

- ```cpp
  class Solution {
  public:
      int rob(vector<int>& nums) {
          int n = nums.size();
          if (n == 1) {
              return nums[0];
          }else if (n == 2) {
              return max(nums[0], nums[1]);
          }
  
          return max(solve(nums, 0, n - 1), solve(nums, 1, n));
      }
  
      int solve(vector<int>& nums, int begin, int end) {
          int first = nums[begin], second = max(nums[begin], nums[begin + 1]);
  
          for (int i = begin + 2; i < end; ++ i) {
              int temp = second;
              second = max(first + nums[i], second);
              first = temp;
          }
  
          return second;
      }
  };
  ```



## 打家劫舍III

- jd：

- ```cpp
  /**
   * Definition for a binary tree node.
   * struct TreeNode {
   *     int val;
   *     TreeNode *left;
   *     TreeNode *right;
   *     TreeNode() : val(0), left(nullptr), right(nullptr) {}
   *     TreeNode(int x) : val(x), left(nullptr), right(nullptr) {}
   *     TreeNode(int x, TreeNode *left, TreeNode *right) : val(x), left(left), right(right) {}
   * };
   */
  class TreeStatus{
      public:
          int select;
          int buselect;
  };
  
  class Solution {
  public:
      int rob(TreeNode* root){
          TreeStatus res = solve(root);
          return max(res.select, res.buselect);
      }
      
      TreeStatus solve(TreeNode* root){
          if (!root){
              return {0, 0};
          }
  
          TreeStatus left = solve(root -> left);
          TreeStatus right = solve(root -> right);
          return {root -> val + left.buselect + right.buselect, max(left.select, left.buselect) + max(right.select, right.buselect)};
      }
  };
  ```





# 区间型dp

- 单词拆分



## 最长重复子数组

- jd：寻找最长重复的子数组

- 和子序列有点像，但是不是一类题，因为数组和序列有本质的区别的..

- ```cpp
  class Solution {
  public:
      int findLength(vector<int>& nums1, vector<int>& nums2) {
          int n = nums1.size(), m = nums2.size();
          int res = 0;
          vector<vector<int>> dp(n + 1, vector<int>(m + 1, 0));
          
          for (int i = 1; i <= n; ++ i) {
              for (int j = 1; j <= m; ++ j) {
                  dp[i][j] = (nums1[i - 1] == nums2[j - 1]) ? 1 + dp[i - 1][j - 1] : 0;
                  res = max(dp[i][j], res);
              }
          }
  
          return res;
      }
  };
  ```



## 回文子串

- jd：查询回文串的数量

- ```cpp
  class Solution {
  public:
      int countSubstrings(string s) {
          int n = s.size();
          int res = 0;
          vector<vector<int>> dp(n, vector<int>(n, 0));
  
          for (int i = 0; i < n; ++ i) {
              for (int j = 0; j + i < n; j ++ ) {
                  if (i == 1) {
                      dp[j][j + i] = (s[j] == s[j + i]) ? 1: 0;
                  }else if (i == 0) {
                      dp[j][j + i] = 1;
                  } else {
                      if (dp[j + 1][j + i - 1] != 0 && s[j] == s[j + i]) {
                          dp[j][j + i] = 1;
                      }
                  }
                  res += dp[j][j + i];
              }
          }
  
          return res;
      }
  };
  ```



## 剑指offer II 020.回文子字符串的个数

- 和回文子串一样（不过有一个更优的做法）



## 最长回文子串

- jd：寻找字串中最长的回文子串

- ```cpp
  class Solution {
  public:
      string longestPalindrome(string s) {
          int n = s.size();
          string res = "";
          vector<vector<int>> dp(n, vector<int> (n, 0));
  
          for (int i = 0; i < n; ++ i ) {
              for (int j = 0; j < n - i; ++ j ) {
                  if (i == 0) {
                      dp[j][j] = 1;
                  } else if (i == 1) {
                      dp[j][j + i] = (s[j + i] == s[j]) ? 2 : 0;
                  } else if (dp[j + 1][j + i - 1] != 0) {
                      dp[j][j + i] = (s[j + i] == s[j]) ? dp[j + 1][j + i - 1] + 2 : 0;
                  }
  
                  // res = (res.size() >= dp[j][j + i]) ? res : s.substr(j, i + 1);//用了这句话就会超时....
                  if (res.size() < dp[j][j + i]) {
                      res = s.substr(j, i + 1);
                  }
              }
          }
  
          return res;
      }
  };
  ```



## 最长回文子序列

- jd：返回最长回文子序列的长度

- ```cpp
  class Solution {
  public:
      int longestPalindromeSubseq(string s) {
          int n = s.size();
          vector<vector<int>> f(n, vector<int> (n, 1));
          for (int i = 0; i < n - 1; ++ i) {
              f[i][i + 1] = (s[i] == s[i + 1] ? 2 : 1);
          }
          
          for (int j = 2; j < n; ++ j) {
              for (int i = 0; i < n - j; ++ i) {
                  f[i][i + j] = max(f[i][i + j - 1], max(f[i + 1][i + j], f[i + 1][i + j - 1]));
                  if (s[i] == s[i + j]){
                      f[i][i + j] = max(2 + f[i + 1][i + j - 1], f[i][i + j]);
                  }
              }
          }
          return f[0][n - 1];
      }
  };
  ```



## 戳气球

- jd：

- 经典的区间型dp

- PS：dp数组的两个边界不参与计算的

- ```cpp
  class Solution {
  public:
      int maxCoins(vector<int>& nums) {
          nums.push_back(1);
          nums.insert(nums.begin(), 1);
          int n = nums.size();
          vector<vector<int>> f(n, vector<int>(n, 0));
          for (int i = 0; i < n - 2; ++ i) {
              f[i][i + 2] = nums[i] * nums[i + 1] * nums[i + 2];
          }
          
          for (int i = 3; i < n; ++ i) {
              for (int j = 0; j < n - i; ++ j) {
                  for (int k = j + 1; k < j + i; ++ k) {
                      f[j][j + i] = max(f[j][j + i], f[j][k] + nums[j] * nums[k] * nums[j + i] + f[k][j + i]);
                  }
              }
          }
  
          return f[0].back();
      }
  };
  ```





# 序列型dp

- 正则表达式
- **编辑距离**
- 交错字符串



## 最长公共子序列

- jd：

- 经典的序列dp，注意一下数组的初始化

- ```cpp
  class Solution {
  public:
      int longestCommonSubsequence(string text1, string text2) {
          int n = text1.size(), m = text2.size();
          vector<vector<int>> dp(n + 1, vector<int> (m + 1, 0));
  
          for (int i = 1; i <= n; ++ i) {
              for (int j = 1; j <= m; ++ j) {
                  dp[i][j] = max(dp[i - 1][j], dp[i][j - 1]);
                  if (text1[i - 1] == text2[j - 1]) {
                      dp[i][j] = max(dp[i][j], dp[i - 1][j - 1] + 1);
                  }
              }
          }
  
          return dp.back().back();
      }
  };
  
  //	优化为滚动数组
  class Solution {
  public:
      int longestCommonSubsequence(string text1, string text2) {
          int n = text1.length(), m = text2.length();
          vector<vector<int>> dp(2, vector<int> (m + 1, 0));
  
          for (int i = 1, now = 0, old = 0; i <= n; ++ i) {
              now = i % 2;
              old = 1 - now;
              for (int j = 1; j <= m; ++ j) {
                  dp[now][j] = max(dp[old][j], dp[now][j - 1]);
                  if (text1[i - 1] == text2[j - 1]) {
                      dp[now][j] = max(dp[now][j], dp[old][j - 1] + 1);
                  }
              }
          }
  
          return dp[n % 2][m];
      }
  };
  
  //  优化至一维数组
  class Solution {
  public:
      int longestCommonSubsequence(string text1, string text2) {
          int n = text1.size(), m = text2.size();
          vector<int> dp(m + 1, 0);
  
          for (int i = 1; i <= n; ++ i) {
              int pre = 0;
              for (int j = 1; j <= m; ++ j) {
                  int temp = dp[j];
                  dp[j] = max(dp[j], dp[j - 1]);
                  if (text1[i - 1] == text2[j - 1]) {
                      dp[j] = max(pre + 1, dp[j]);
                  }
                  pre = temp;
              }
          }
  
          return dp[m];
      }
  };
  ```







# Others

- 接雨水
- 俄罗斯套娃信封问题
- 鸡蛋掉落
- 剑指offer n个骰子的点数
- 不同的二叉搜索树



## 解码问题

- jd：

- ```cpp
  class Solution {
  public:
      int numDecodings(string s) {
          int n = s.size();
          vector<int> dp(n + 1, 0);
          dp[0] = 1;
  
          for (int i = 1; i <= n; ++ i) {
              if (s[i - 1] != '0') {
                  dp[i] += dp[i - 1];
              }
              if (i > 1 && s[i - 2] != '0' && ((s[i - 2] - '0') * 10 + (s[i - 1] - '0') <= 26)) {
                  dp[i] += dp[i - 2];
              }
          }
  
          return dp[n];
      }
  };
  
  //滚动数组优化
  class Solution {
  public:
      int numDecodings(string s) {
          int n = s.size();
          int dp1 = 0, dp2 = 1;
  
          for (int i = 0; i < n; ++ i) {
              int temp = 0;
              if (s[i] != '0') {
                  temp += dp2;
              }
              if (i > 0 && s[i - 1] != '0' && ((s[i - 1] - '0') * 10 + (s[i] - '0')) < 27) {
                  temp += dp1;
              }
              dp1 = dp2;
              dp2 = temp;
          }
  
          return dp2;
      }
  };
  ```



## 整数拆分

- jd：

- ```cpp
  class Solution {
  public:
      int integerBreak(int n) {
          vector<int> dp(n + 1, 0);
          dp[1] = 1;
  
          for (int i = 1; i <= n; ++ i) {
              for (int j = 1; j < i; ++ j) {
                  dp[i] = max(dp[i], max(j * (i - j), j * dp[i - j]));
              }
          }
  
          return dp[n];
      }
  };
  
  //数学方法优化
  class Solution {
  public:
      int integerBreak(int n) {
          if (n < 4) {
              return n - 1;
          }
          
          vector<int> dp(n + 1, 1);
          for (int i = 3; i <= n; ++ i) {
              dp[i] = max(2 * max(i - 2, dp[i - 2]), 3 * max(i - 3, dp[i - 3]));
          }
  
          return dp[n];
      }
  };
  ```



## 最大子序列和

- 同剑指offer 42.连续子数组的最大和

- 简单题，但是思路却很巧妙
- 先初始化dp为第一个元素
- 对于后面的每一个元素，如果我当前的dp是正的话，那我就加上当前的数；否则dp就变为当前的数（这一步非常的关键，可以认为是一种贪心的做法，因为dp为正的时候，它可以搏一搏更大的数，因为后面如果是正的，就更大了；如果负的，那么首先res已经记录了max值，其次，加上负的，有可能后面还会有更大的数。这无疑是一种贪心了）
- 然后将此时的dp和res进行比较，res去max
- 最后遍历完所有的元素后，return res



## 斐波那契数

- ```cpp
  //递归写法
  class Solution {
  public:
      int fib(int n) {
          if (n == 1 || n == 0){
              return n;
          }else{
              return fib(n - 1) + fib(n - 2);
          }
      }
  };
  
  //滚动数组
  class Solution {
  public:
      int fib(int n) {
          int first = 0, second = 1;
  
          for (int i = 2; i <= n; ++ i) {
              int mid = second;
              second += first;
              first = mid;
          }
  
          return n == 0 ? 0 : second;
      }
  };
  ```



## 爬楼梯

- ```cpp
  class Solution {
  public:
      int climbStairs(int n) {
          int dp[2] = {1, 1}; // 使用数组能够提高cpu cache的s
  
          for (int i = 2; i <= n; ++ i) {
              int temp = dp[1];
              dp[1] += dp[0];
              dp[0] = temp;
          }
  
          return dp[1];
      }
  };
  ```



## 完全平方数

- jd：

- ```cpp
  class Solution {
  public:
      int numSquares(int n) {
          vector<int> dp(n + 1, INT_MAX);
          dp[0] = 0;
  
          for (int i = 1; i <= n; ++ i) {
              for (int j = 1; j * j <= i; ++ j) {
                  dp[i] = min(dp[i], dp[i - j * j] + 1);
              }
          }
  
          return dp[n];
      }
  };
  ```



## 不同二叉搜索树

- jd：

- ```cpp
  class Solution {
  public:
      int numTrees(int n) {
          if (n < 3) {
              return n;
          }
          vector<int> dp(n + 1, 0);
          dp[0] = 1;
  
          for (int i = 1; i <= n; ++ i) {
              for (int j = 0; j < i; ++ j) {
                  dp[i] += (dp[i - j - 1] * dp[j]);
              }
          }
  
          return dp[n];
      }
  };
  ```





## 目标和

- jd：这道题经典之处在于它的数学上的推导，非常值得品味

- ```cpp
  // 二维dp
  class Solution {
  public:
      int findTargetSumWays(vector<int>& nums, int target) {
          int sum = accumulate(nums.begin(), nums.end(), 0), diff = sum - target;
  
          if (diff < 0 || diff % 2 != 0) {
              return 0;
          }
  
          int n = nums.size(), neg = diff / 2;
          vector<vector<int>> dp(2, vector<int>(neg + 1));
          dp[0][0] = 1;
  
          for (int i = 1, now = 0, old = 0; i <= n; ++ i ) {
              now = i % 2;
              old = 1 - now;
              int num = nums[i - 1];
              for (int j = 0; j <= neg; ++ j) {
                  dp[now][j] = dp[old][j];
                  if (j >= num) {
                      dp[now][j] += dp[old][j - num];
                  }
              }
          }
  
          return dp[n % 2][neg];
      }
  };
  
  // 压缩dp
  class Solution {
  public:
      int findTargetSumWays(vector<int>& nums, int target) {
          int sum = accumulate(nums.begin(), nums.end(), 0), diff = sum - target;
  
          if (diff < 0 || diff % 2 != 0) {
              return 0;
          }
  
          int n = nums.size(), neg = diff / 2;
          vector<int> dp(neg + 1, 0);
          dp[0] = 1;
  
          for (int i = 0; i < n; ++ i ) {
              for (int j = neg; j >= 0; -- j) {
                  if (j >= nums[i]) {
                      dp[j] += dp[j - nums[i]];
                  }
              }
          }
  
          return dp[neg];
      }
  };
  ```



## 丑数II

- jd:

- 其实也不能算是dp，但是当前每次位置数量的更新都是要依靠前面的数字的，就勉强算是dp吧

- ```cpp
  class Solution {
  public:
      int nthUglyNumber(int n) {
          // 该方法的证明过程复杂，直接背题目就行了
          vector<int> dp(n + 1, 1);
          int p2 = 1, p3 = 1, p5 = 1;
  
          for (int i = 2; i <= n; ++ i) {
              int num2 = dp[p2] * 2, num3 = dp[p3] * 3, num5 = dp[p5] * 5;
              dp[i] = min(min(num2, num3), num5);
              if (dp[i] == num2) {
                  ++ p2;
              }
  
              if (dp[i] == num3) {
                  ++ p3;
              }
              
              if (dp[i] == num5) {
                  ++ p5;
              }
          }
  
          return dp[n];
      }
  };
  ```



## 掷骰子的N种方法



## 组合总和 Ⅳ



## 分割等和子集



## 最后一块石头的重量 II



# 总结

- 题目如果涉及到区间的，马上想到区间型动态规划
  - 解：首先是确定区间i-j，然后在i-j里面选择数字k，查看i-k和k+1-j的情况，然后把状态转移给i-j
  - 注意要控制好循环的边界，同时做好dp数组的初始化
- 而区间型的dp，看看是否可以用背包问题来优化一下
  - 例如单词拆分，用区间是可以做出来，但是时间空间的效率都太慢了
  - 所以思考一下对于0-i之间的字母，如果可以用dictionary组合出来，必然存在j，使得j-i之间为一个在dictionary里面的单词
  - 而要保证0-i之间为true，就要保证后面是一个单词，并且前面也要是true
  - 这就是最早的硬币问题啦
- 而股票问题给我们最大的启示就是
  - 首先，要找到正确的状态去转移，题目往往会给很多无用的信息
  - 如果状态的维数太高，考虑是不是要降维换成数组来表示（如三维数组变为sold和hold两个数组）

- dp的几个关键点
  - 将问题转换为子问题，由此实现状态的步步转移（比如说最后一步的结果，是由前面的那几步推导过来的）
  - 写出状态转移方程
  - 初始化数组（这一步很重要，这会直接导致后续的bug）
  - 得到结果，然后查看是否能够使用滚动数组进行优化，即降维处理



# 滚动数组优化

- 思路：可以用first和second，或者temp来实现，或者使用二进制来实现
- PS：其实能用数组就用数组，因为这样会减少cache miss，提高效率（不过打家劫舍II就不能用二进制数组，坑很大）
- 例题：
  - 62、不同路径
  - 63、不同路径II
  - 64、最小路径和
  - 120、最小三角路径和
  - 198、打家劫舍
  - 213、打家劫舍II（这里只能用第一种方法来实现滚动数组，小心坑）
- 滚动数组优化的一个要点：每次计算之后，都要重置一遍前面的几个滚动变量
  - 比如解码问题中的滚动变量，计算完后，第一个变量应该是下一个变量的前两个变量，第二个变量和第三个变量都是下一个变量的前一个变量
- 什么时候滚动数组是一维数组，什么时候是二维数组
  - 一般来说，大多数的滚动数组到最后都可以优化到一维数组的情况（如果需要更新后同一行的数据和上一行当前位置的数据，就从左往右循环；否则需要只上一行的数据和当前行的数据，就从右往左循环）
  - 那些不能优化到一维数组的要么就是优化后代码的可读性太差，要么就是状态方程需要上下两行数组来更新状态，导致不能用一维（比如说有一个二维数组，更新方式是从右往左循环的，新的dp[1] [j]既需要dp[0] [j-k]也需要dp[1] [j-k]，那么此时就不能优化到一维数组了，因为一维数组会把原来的dp[0] [j-k]给cover掉）
  - 当然，大部分的dp要的只是上一行的数据，需要上两行的着实罕见喵







# dp数组初始化

- 数组的下标从1开始能够解决很多边界问题
- 求最大或者最小的时候，数组初始化最好反方向设置，比如说求最小的xx时，就init为INT_MAX





# 思路

- 将问题分解为子问题，比如说要达到最后一个目标，需要得到哪几个目标
- 由子问题写出状态转移方程
- 用循环遍历出方程
- 初始化dp数组
- 想办法优化，比如说滚动数组
