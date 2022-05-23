// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "tellor-io/usingtellor@4.0.6/contracts/UsingTellor.sol";
import "../interfaces/IAutopay.sol";
import "../interfaces/IERC20.sol";

contract KeeprTellor is UsingTellor {

    IAutopay public autopay;
    IERC20 public tellorToken;
    uint256 public tipAmount;
    
    /**
    * @dev Initializes parameters
    * @param _tellor address of tellor oracle contract
    * @param _autopay address of tellor autopay contract
    */
    constructor(address payable _tellor, address _autopay, address _tellorToken, uint256 _tipAmount) UsingTellor(_tellor) {
        autopay = IAutopay(_autopay);
        tellorToken = IERC20(_tellorToken);
        tipAmount = _tipAmount;
    }

    function tip_request(
        bytes calldata _function, 
        address _targetContract,
        uint256 _timestampToTrigger,
        uint256 _chainId,
        uint256 _tipAmount) external {
            bytes memory _queryData = abi.encode("TellorKpr",abi.encode(_function,_targetContract,_timestampToTrigger,_chainId)); 
            bytes32  _queryId = keccak256(_queryData);
            // is it possible to calculate the gas cost of function signature if gasCalculate(_function)
            // to ensure _tipAmount is more than the gas costs.
            // to create incentive tipamount has to be greater.
            tellorToken.approve(address(autopay), _tipAmount);
            autopay.tip(_queryId,_tipAmount,_queryData);
        }

    function fundCallFeed(bytes calldata _function, 
    address _targetContract,
    uint256 _timestampToTrigger, 
    uint256 _chainId,
    uint256 _startTime,
    uint256 _reward, 
    uint256 _interval, 
    uint256 _window,
    uint256 _tipAmount) external {
        bytes memory _queryData = abi.encode("TellorKpr",abi.encode(_function,_targetContract,_timestampToTrigger,_chainId)); 
        bytes32 _queryId = keccak256((_queryData));
        bytes memory _feedData = abi.encode(_queryId, _reward, _startTime, _interval, _window, 0);
        bytes32 _feedId = keccak256((_feedData));
        autopay.setupDataFeed(_queryId,_reward,_startTime,_interval,_window,0,_queryData); // priceThreshold set to zero
        // can you estimate gas cost to consider with tip amount
        tellorToken.approve(address(autopay), _tipAmount);
        autopay.fundFeed(_feedId, _queryId, _tipAmount);
        require(_tipAmount > _reward, "tip amount lt reward");
        
    }
    
    function feed_balance(bytes32 _feedId) external view returns (uint256) {
        IAutopay.FeedDetails memory _detail = autopay.getDataFeed(_feedId);

        uint256 _balance = _detail.balance;
        return _balance;
        
     }
}