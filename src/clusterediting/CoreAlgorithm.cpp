#include "CoreAlgorithm.h"

using NodeId = DynamicSparseGraph::NodeId;

/**
    * Generates a set of solutions from its internal parameters (instance and parameter set)
    * @return The solution set as CES*
    */
ClusterEditingSolutionLight CoreAlgorithm::run() {
    // Split graph into components
//     if (verbosity > 1) {
//         std::cout << "Splitting the graph into connected components ..." << std::endl;
//     }
//     
//     std::vector<std::vector<NodeId>> components = graph.getPositiveComponentes();
//     std::vector<std::vector<NodeId>> clusters;
//     double totalCost = 0.0;
//     
//     if (verbosity > 1) {
//         std::cout<<"Found "<<components.size()<<" connected components."<< std::endl;
//     }
//     
//     // Run one instance per connected component
//     for (std::vector<NodeId> component : components) {
//         
//         if (component.size() <= 2) {
//             // trivial solution for up to two nodes
//             clusters.push_back(std::vector<NodeId>(component.begin(), component.end()));
//         } else {
//             // create static subgraph and solve cluster editing on it
//             StaticSparseGraph subgraph(graph, component);
//             InducedCostHeuristic instance(subgraph, bundleEdges);
//             ClusterEditingSolutionLight subSol = instance.solve();
//             
//             // add local clusters to final clustering
//             totalCost += subSol.getTotalCost();
//             for (unsigned int i = 0; i < subSol.getNumClusters(); i++) {
//                 std::vector<NodeId> cluster;
//                 for (NodeId v : subSol.getCluster(i)) {
//                     // instance's node ids must be mapped back to global node ids
//                     cluster.push_back(component[v]);
//                     
//                 }
//                 clusters.push_back(cluster);
//             }
//         }
//         if (verbosity > 1) {
//             std::cout<<"Solved sub-instance with "<<component.size()<<" nodes."<<std::endl;
//         }
//     }
//     
//     ClusterEditingSolutionLight solution(totalCost, clusters);
    
    StaticSparseGraph sGraph(graph);
    InducedCostHeuristic instance(sGraph, bundleEdges);
    ClusterEditingSolutionLight solution = instance.solve();
    
    if (verbosity > 2) {
        std::cout<<"Number of clusters:\t"<<solution.getNumClusters()<<std::endl;
        std::cout<<"Total editing cost:\t"<<solution.getTotalCost()<<std::endl;
    }

    return solution;
}
