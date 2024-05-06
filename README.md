# arbera research

https://0xidm.github.io/arbera-research/parameters.html

## Definitions

# Arbera Parameters

- **wrap fee**: realized when users wrap token into pod
- **unwrap fee**: realized when users unwrap token into pod.
    - Users can use the below formula to determine the quantity of TKN they can expect to receive when unwrapping pTKN; `(pTKN * CBR) * (100% - Unwrap Fee%)`
- **burn percent**: The rate at which pod fees increase the vault share of collaterlized assets per pod token. The higher the burn fee the more pTKN holders benefit and less yield is generated for pTKN LPs
- **buy fee**: This fee determines if buying pod tokens from the liquidity pool staked users are LPing to earn yield in incurs a fee.
- **sell fee**: This fee determines if selling pod tokens from the liquidity pool staked users are LPing to earn yield in incurs a fee.
- **partner fee**: This fee allows the pod creator to realize a small portion of pod tokens back for all volume through the pod.
- **collateral backing ratio**: The change in pod token collateral backing since pod creation that starts at 1. If the backing ratio is 1.1, this means there is 1.1 TKN per pTKN in the pod.
- **LP TVL**: Obtained from Uniswap pToken pool; staked pTOKEN in USD + staked pairTOKEN in USD
- **TVL**: Obtained from pTOKEN total supply value in USD + staked pairTOKEN in USD
- **Fair Price**: Price to obtain underlying token from DEX
- **Pod Price**: Price to obtain pToken
- **CBR APR (Holder APR)**: represents return for pTOKEN holders as a result of burn byproducts
- **LP APR**: return obtained through fees from LPing (i.e. from providing LP to Camelot or Uniswap)
- **WeightedIndex**: pTOKEN is ERC20 compatible "wrapped token" created for/by the Pod; holds TOKENs as they are wrapped
- **StakingPoolToken**: spTOKEN is the contract that holds CMLT-LP tokens on behalf of the Pod
- **CamelotPair**: CMLT-LP representing paired liquidity for the pTOKEN; holds pTOKEN and paired pASSET; the Pod might not hold all the LP
