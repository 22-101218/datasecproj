// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract VehicleOwnership {
    address public immutable authority;

    struct Vehicle {
        string vehicleId;
        string brand;
        string model;
        address currentOwner;
        uint256 registeredAt;
        bool exists;
    }

    struct OwnershipRecord {
        address owner;
        uint256 transferredAt;
    }

    mapping(string => Vehicle) private vehicles;
    mapping(string => OwnershipRecord[]) private ownershipHistory;
    mapping(address => bool) public verifiers;

    event VehicleRegistered(
        string indexed vehicleId,
        string brand,
        string model,
        address indexed owner,
        uint256 registeredAt
    );
    event OwnershipTransferred(
        string indexed vehicleId,
        address indexed previousOwner,
        address indexed newOwner,
        uint256 transferredAt
    );
    event OwnershipVerified(
        string indexed vehicleId,
        address indexed verifier,
        address owner,
        uint256 verifiedAt
    );
    event VerifierUpdated(address indexed verifier, bool allowed);

    modifier onlyAuthority() {
        require(msg.sender == authority, "Only authority allowed");
        _;
    }

    modifier onlyVerifier() {
        require(verifiers[msg.sender], "Only verifier allowed");
        _;
    }

    modifier vehicleMustExist(string memory vehicleId) {
        require(vehicles[vehicleId].exists, "Vehicle not found");
        _;
    }

    modifier onlyVehicleOwner(string memory vehicleId) {
        require(
            msg.sender == vehicles[vehicleId].currentOwner,
            "Only current owner can transfer"
        );
        _;
    }

    constructor() {
        authority = msg.sender;
    }

    function setVerifier(address verifier, bool allowed) external onlyAuthority {
        verifiers[verifier] = allowed;
        emit VerifierUpdated(verifier, allowed);
    }

    function registerVehicle(
        string calldata vehicleId,
        string calldata brand,
        string calldata model,
        address owner
    ) external onlyAuthority {
        require(bytes(vehicleId).length > 0, "Vehicle ID required");
        require(!vehicles[vehicleId].exists, "Vehicle already registered");
        require(owner != address(0), "Invalid owner address");

        vehicles[vehicleId] = Vehicle({
            vehicleId: vehicleId,
            brand: brand,
            model: model,
            currentOwner: owner,
            registeredAt: block.timestamp,
            exists: true
        });

        ownershipHistory[vehicleId].push(
            OwnershipRecord({owner: owner, transferredAt: block.timestamp})
        );

        emit VehicleRegistered(vehicleId, brand, model, owner, block.timestamp);
    }

    function transferOwnership(
        string calldata vehicleId,
        address newOwner
    )
        external
        vehicleMustExist(vehicleId)
        onlyVehicleOwner(vehicleId)
    {
        require(newOwner != address(0), "Invalid new owner address");

        Vehicle storage v = vehicles[vehicleId];
        require(newOwner != v.currentOwner, "Owner unchanged");

        address previousOwner = v.currentOwner;
        v.currentOwner = newOwner;

        ownershipHistory[vehicleId].push(
            OwnershipRecord({owner: newOwner, transferredAt: block.timestamp})
        );

        emit OwnershipTransferred(
            vehicleId,
            previousOwner,
            newOwner,
            block.timestamp
        );
    }

    function verifyCurrentOwner(
        string calldata vehicleId
    ) external view vehicleMustExist(vehicleId) returns (address) {
        return vehicles[vehicleId].currentOwner;
    }

    function verifyOwnershipByVerifier(
        string calldata vehicleId
    ) external vehicleMustExist(vehicleId) onlyVerifier returns (address) {
        address owner = vehicles[vehicleId].currentOwner;
        emit OwnershipVerified(vehicleId, msg.sender, owner, block.timestamp);
        return owner;
    }

    function getVehicle(
        string calldata vehicleId
    )
        external
        view
        vehicleMustExist(vehicleId)
        returns (
            string memory,
            string memory,
            string memory,
            address,
            uint256
        )
    {
        Vehicle memory v = vehicles[vehicleId];
        return (v.vehicleId, v.brand, v.model, v.currentOwner, v.registeredAt);
    }

    function getOwnershipHistory(
        string calldata vehicleId
    )
        external
        view
        vehicleMustExist(vehicleId)
        returns (OwnershipRecord[] memory)
    {
        return ownershipHistory[vehicleId];
    }
}
